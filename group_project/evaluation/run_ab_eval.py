"""A/B evaluation cho retrieval: Config A (dense-only) vs Config B (hybrid + RRF).

Chạy:
    python -m group_project.evaluation.run_ab_eval --top-k 5

Hai config dùng chung golden dataset, generator, prompt, evaluator và top_k;
chỉ khác retrieval strategy (``use_reranking``). Kết quả thô được ghi ra
``ab_results.json`` để RESULT.md trích số liệu.
"""

import argparse
import json
import os
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

EVAL_DIR = ROOT / "group_project" / "evaluation"
GOLDEN = EVAL_DIR / "golden_dataset.json"

CONFIGS = {
    "A": {"label": "dense-only", "use_reranking": False},
    "B": {"label": "hybrid + RRF", "use_reranking": True},
}

_last_call = 0.0


def _throttle(min_interval: float) -> None:
    """Giữ khoảng cách tối thiểu giữa hai lần gọi API để tránh rate limit."""
    global _last_call
    wait = min_interval - (time.time() - _last_call)
    if wait > 0:
        time.sleep(wait)
    _last_call = time.time()


def generate_answer(query: str, chunks: list[dict], min_interval: float) -> str:
    """Dùng đúng prompt/generator của Task 10 trên chunks đã truy xuất."""
    from src.task10_generation import (
        SAFE_REFUSAL,
        SYSTEM_PROMPT,
        call_llm,
        format_context,
        reorder_for_llm,
    )

    if not chunks:
        return SAFE_REFUSAL
    context = format_context(reorder_for_llm(chunks))
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    attempts = 8
    for attempt in range(attempts):
        _throttle(min_interval)
        try:
            answer = call_llm(SYSTEM_PROMPT, user_message)
            if answer:
                return answer
        except Exception as error:  # rate limit hoặc provider lỗi tạm thời
            if attempt == attempts - 1:
                raise
            print(f"    retry {attempt + 1}: {type(error).__name__}: {str(error)[:120]}")
            time.sleep(min(65.0, 5 * 2 ** attempt))
    return SAFE_REFUSAL


def ensure_index() -> int:
    from src.task4_chunking_indexing import get_collection, run_pipeline

    collection = get_collection()
    if collection.count() == 0:
        print("Collection rong -> chay lai chunking/indexing")
        run_pipeline()
        collection = get_collection()
    return collection.count()


def run_config(
    config_key: str,
    golden: list[dict],
    top_k: int,
    min_interval: float,
    done: list[dict] | None = None,
    save_checkpoint=None,
) -> list[dict]:
    from src.task9_retrieval_pipeline import retrieve

    config = CONFIGS[config_key]
    records = list(done or [])
    answered = {record["question"] for record in records}
    for index, case in enumerate(golden, 1):
        question = case["question"]
        if question in answered:
            print(f"  [{config_key}] {index}/{len(golden)} (checkpoint) {question[:40]}")
            continue
        start = time.perf_counter()
        chunks = retrieve(question, top_k=top_k, use_reranking=config["use_reranking"])
        retrieval_latency = time.perf_counter() - start

        start = time.perf_counter()
        answer = generate_answer(question, chunks, min_interval)
        generation_latency = time.perf_counter() - start

        records.append(
            {
                "config": config_key,
                "question": question,
                "reference": case["expected_answer"],
                "expected_context": case["expected_context"],
                "source": case.get("source", ""),
                "answer": answer,
                "retrieved_ids": [chunk["id"] for chunk in chunks],
                "retrieved_contexts": [chunk["content"] for chunk in chunks],
                "retrieval_method": chunks[0]["retrieval_method"] if chunks else "none",
                "top_score": round(float(chunks[0]["score"]), 6) if chunks else 0.0,
                "retrieval_latency_s": round(retrieval_latency, 3),
                "generation_latency_s": round(generation_latency, 3),
                "total_latency_s": round(retrieval_latency + generation_latency, 3),
            }
        )
        if save_checkpoint is not None:
            # Quota cua provider co gioi han theo ngay: luu ngay sau moi case de
            # lan chay lai khong ton them request cho case da thanh cong.
            save_checkpoint(config_key, records)
        print(f"  [{config_key}] {index}/{len(golden)} {question[:52]}")

    order = {case["question"]: position for position, case in enumerate(golden)}
    records.sort(key=lambda record: order.get(record["question"], len(order)))
    return records


def build_evaluator(model: str, max_workers: int, evaluator_rpm: float):
    from langchain_core.embeddings import Embeddings
    from langchain_core.rate_limiters import InMemoryRateLimiter
    from langchain_openai import ChatOpenAI
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.run_config import RunConfig

    from src.task4_chunking_indexing import embed_texts

    class PipelineEmbeddings(Embeddings):
        """Dùng đúng embedding model của pipeline cho answer relevance."""

        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            return embed_texts(list(texts))

        def embed_query(self, text: str) -> list[float]:
            return embed_texts([text])[0]

    # Free tier cua Gemini gioi han 15 RPM cho flash-lite; ragas chay song song
    # nen phai chan toc do o tang client, khong chi giam max_workers.
    rate_limiter = InMemoryRateLimiter(
        requests_per_second=evaluator_rpm / 60.0,
        check_every_n_seconds=0.2,
        max_bucket_size=max(1, max_workers),
    )
    evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model=model,
            api_key=os.environ["GEMINI_API_KEY"],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            temperature=0.0,
            max_retries=8,
            timeout=120,
            rate_limiter=rate_limiter,
        )
    )
    run_config = RunConfig(timeout=300, max_retries=15, max_wait=90, max_workers=max_workers)
    return evaluator_llm, LangchainEmbeddingsWrapper(PipelineEmbeddings()), run_config


def evaluate_records(
    records: list[dict], model: str, max_workers: int, evaluator_rpm: float
) -> list[dict]:
    from ragas import EvaluationDataset, SingleTurnSample, evaluate
    from ragas.metrics import (
        Faithfulness,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
        ResponseRelevancy,
    )

    evaluator_llm, evaluator_embeddings, run_config = build_evaluator(
        model, max_workers, evaluator_rpm
    )
    metrics = [
        Faithfulness(llm=evaluator_llm),
        # strictness=1: endpoint OpenAI-compat cua Gemini khong cho sampling nhieu
        # candidate (n>1); cung tham so nay duoc dung cho ca hai config.
        ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings, strictness=1),
        LLMContextRecall(llm=evaluator_llm),
        LLMContextPrecisionWithReference(llm=evaluator_llm),
    ]
    dataset = EvaluationDataset(
        samples=[
            SingleTurnSample(
                user_input=record["question"],
                response=record["answer"],
                retrieved_contexts=record["retrieved_contexts"],
                reference=record["reference"],
            )
            for record in records
        ]
    )
    result = evaluate(dataset=dataset, metrics=metrics, run_config=run_config, show_progress=True)
    frame = result.to_pandas()
    columns = {
        "faithfulness": "faithfulness",
        "answer_relevancy": "answer_relevancy",
        "context_recall": "context_recall",
        "context_precision": "llm_context_precision_with_reference",
    }
    scored = []
    for record, (_, row) in zip(records, frame.iterrows()):
        scores = {}
        for name, column in columns.items():
            value = row.get(column)
            scores[name] = None if value is None or value != value else round(float(value), 4)
        scored.append({**record, "scores": scores})
    return scored


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(fraction * len(ordered))) - 1))
    return ordered[index]


def aggregate(scored: list[dict]) -> dict:
    metrics = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
    summary = {}
    for metric in metrics:
        values = [item["scores"][metric] for item in scored if item["scores"].get(metric) is not None]
        summary[metric] = round(statistics.fmean(values), 4) if values else None
    available = [summary[metric] for metric in metrics if summary[metric] is not None]
    summary["average"] = round(statistics.fmean(available), 4) if available else None

    totals = [item["total_latency_s"] for item in scored]
    retrieval = [item["retrieval_latency_s"] for item in scored]
    summary["latency"] = {
        "retrieval_p50": round(statistics.median(retrieval), 3),
        "retrieval_p95": round(_percentile(retrieval, 0.95), 3),
        "end_to_end_p50": round(statistics.median(totals), 3),
        "end_to_end_p95": round(_percentile(totals, 0.95), 3),
    }
    summary["scored_cases"] = len(scored)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--limit", type=int, default=0, help="Chi chay N case dau (pilot)")
    parser.add_argument("--rpm", type=float, default=12.0, help="Gioi han request/phut cho generator")
    parser.add_argument("--evaluator-model", default="gemini-3.5-flash-lite")
    parser.add_argument(
        "--generator-model",
        default="",
        help="Ghi de LLM_MODEL khi model trong .env het quota",
    )
    parser.add_argument("--max-workers", type=int, default=3)
    parser.add_argument(
        "--evaluator-rpm",
        type=float,
        default=13.0,
        help="Gioi han request/phut cho evaluator (free tier flash-lite: 15)",
    )
    parser.add_argument("--output", default=str(EVAL_DIR / "ab_results.json"))
    parser.add_argument("--generations", default=str(EVAL_DIR / "ab_generations.json"))
    parser.add_argument("--reuse-generations", action="store_true")
    parser.add_argument("--skip-eval", action="store_true")
    args = parser.parse_args()

    if args.generator_model:
        # task10_generation doc LLM_MODEL luc import, nen phai set truoc khi import.
        os.environ["LLM_MODEL"] = args.generator_model

    min_interval = 60.0 / args.rpm if args.rpm > 0 else 0.0
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    if args.limit:
        golden = golden[: args.limit]

    generations_path = Path(args.generations)
    checkpoint: dict[str, list[dict]] = {}
    if generations_path.exists():
        checkpoint = json.loads(generations_path.read_text(encoding="utf-8"))

    complete = all(len(checkpoint.get(key, [])) == len(golden) for key in CONFIGS)
    if checkpoint and (args.reuse_generations or complete):
        generations = checkpoint
        print(f"Dung lai generations tu {generations_path.name}")
    else:
        chunk_count = ensure_index()
        print(f"Index san sang: {chunk_count} chunks; golden cases: {len(golden)}")
        # Warm-up: lan embed dau tien phai load model, khong tinh vao latency do duoc.
        from src.task9_retrieval_pipeline import retrieve as _warmup_retrieve

        _warmup_retrieve(golden[0]["question"], top_k=args.top_k)
        generations = {key: checkpoint.get(key, []) for key in CONFIGS}

        def save_checkpoint(config_key: str, records: list[dict]) -> None:
            generations[config_key] = records
            generations_path.write_text(
                json.dumps(generations, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        for config_key in CONFIGS:
            print(f"Config {config_key} - {CONFIGS[config_key]['label']}")
            generations[config_key] = run_config(
                config_key,
                golden,
                args.top_k,
                min_interval,
                done=generations[config_key],
                save_checkpoint=save_checkpoint,
            )
        generations_path.write_text(
            json.dumps(generations, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Saved generations -> {generations_path.name}")

    if args.skip_eval:
        return

    payload = {
        "run": {
            "top_k": args.top_k,
            "golden_dataset_size": len(golden),
            "generator_model": os.getenv("LLM_MODEL", ""),
            "generator_provider": os.getenv("LLM_PROVIDER", ""),
            "evaluator_model": args.evaluator_model,
            "evaluator_rpm_limit": args.evaluator_rpm,
            "embedding_model": os.getenv("EMBEDDING_MODEL", ""),
            "score_threshold": os.getenv("SCORE_THRESHOLD", ""),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "configs": {},
    }
    for config_key, records in generations.items():
        print(f"Danh gia Ragas cho config {config_key}")
        scored = evaluate_records(
            records, args.evaluator_model, args.max_workers, args.evaluator_rpm
        )
        payload["configs"][config_key] = {
            "label": CONFIGS[config_key]["label"],
            "summary": aggregate(scored),
            "cases": scored,
        }
        print(json.dumps(payload["configs"][config_key]["summary"], ensure_ascii=False))

    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved -> {args.output}")


if __name__ == "__main__":
    main()
