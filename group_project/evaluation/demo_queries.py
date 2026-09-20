"""Demo end-to-end: một query đúng domain và một query ngoài domain.

Chạy:
    python -m group_project.evaluation.demo_queries

Script gọi đúng hàm mà Streamlit app dùng (``generate_with_citation``) nên
kết quả in ra trùng với những gì chatbot hiển thị, kể cả danh sách nguồn.
Transcript được ghi vào ``group_project/evaluation/DEMO.md``.
"""

import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

OUTPUT_MD = ROOT / "group_project" / "evaluation" / "DEMO.md"
OUTPUT_JSON = ROOT / "group_project" / "evaluation" / "demo_results.json"

IN_DOMAIN_QUERY = "Điều kiện CGPA để duy trì học bổng toàn phần là gì?"
OUT_OF_DOMAIN_QUERY = "Cách nấu phở bò truyền thống ngon nhất là gì?"


def run_query(label: str, query: str, top_k: int = 5) -> dict:
    from src.task10_generation import generate_with_citation
    from src.task5_semantic_search import semantic_search

    dense = semantic_search(query, top_k=1)
    best_dense_score = float(dense[0]["score"]) if dense else 0.0

    start = time.perf_counter()
    result = generate_with_citation(query, top_k=top_k)
    latency = time.perf_counter() - start

    return {
        "label": label,
        "query": query,
        "best_dense_score": round(best_dense_score, 4),
        "answer": result["answer"],
        "retrieval_source": result["retrieval_source"],
        "latency_s": round(latency, 3),
        "sources": [
            {
                "id": source["id"],
                "title": source["metadata"]["title"],
                "source_file": source["metadata"]["source"],
                "url": source["metadata"].get("url"),
                "score": round(float(source["score"]), 6),
                "retrieval_method": source["retrieval_method"],
            }
            for source in result["sources"]
        ],
    }


def render(record: dict) -> str:
    lines = [
        f"## {record['label']}",
        "",
        f"**Query:** {record['query']}",
        "",
        f"- Best dense cosine score: `{record['best_dense_score']}`",
        f"- `retrieval_source`: `{record['retrieval_source']}`",
        f"- Latency: {record['latency_s']}s",
        "",
        "**Answer:**",
        "",
        "```text",
        record["answer"],
        "```",
        "",
        "**Nguồn được trả về (đúng những gì UI hiển thị):**",
        "",
    ]
    if not record["sources"]:
        lines.append("Không có nguồn nào được trả về (safe refusal).")
    else:
        lines.append("| # | Chunk ID | Title | Score | Method |")
        lines.append("| --: | --- | --- | --: | --- |")
        for index, source in enumerate(record["sources"], 1):
            lines.append(
                f"| {index} | `{source['id']}` | {source['title']} | "
                f"{source['score']:.4f} | {source['retrieval_method']} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    records = [
        run_query("Query 1 — trong domain", IN_DOMAIN_QUERY),
        run_query("Query 2 — ngoài domain", OUT_OF_DOMAIN_QUERY),
    ]
    header = [
        "# Demo transcript",
        "",
        f"Chạy lúc {time.strftime('%Y-%m-%d %H:%M:%S')} bằng "
        "`python -m group_project.evaluation.demo_queries`.",
        "",
        f"- Generator: `{os.getenv('LLM_MODEL', '')}` "
        f"(provider `{os.getenv('LLM_PROVIDER', '')}`)",
        f"- Embedding: `{os.getenv('EMBEDDING_MODEL', '')}`",
        f"- `SCORE_THRESHOLD`: `{os.getenv('SCORE_THRESHOLD', '')}`, `top_k` = 5",
        "- Retrieval: hybrid (dense + BM25 + RRF) như cấu hình mặc định của chatbot",
        "",
        "",
    ]
    OUTPUT_MD.write_text(
        "\n".join(header) + "\n".join(render(record) for record in records), encoding="utf-8"
    )
    OUTPUT_JSON.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for record in records:
        print(render(record))
    print(f"Saved -> {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
