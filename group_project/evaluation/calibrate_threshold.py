"""Hiệu chỉnh SCORE_THRESHOLD bằng query in-domain và out-of-domain.

Chạy:
    python -m group_project.evaluation.calibrate_threshold

Script chỉ dùng dense retrieval (cosine similarity gốc) vì fallback trong
``retrieve()`` so sánh threshold với best dense score, không phải RRF score.
"""

import json
import statistics
from pathlib import Path

from src.task5_semantic_search import semantic_search


ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "group_project" / "evaluation" / "golden_dataset.json"
OUTPUT = ROOT / "group_project" / "evaluation" / "threshold_calibration.json"

OUT_OF_DOMAIN_QUERIES = [
    "Cách nấu phở bò truyền thống ngon nhất là gì?",
    "Giá vé máy bay Hà Nội đi Đà Nẵng tháng này bao nhiêu?",
    "Làm sao cài đặt Docker trên Ubuntu 22.04?",
    "Đội tuyển Việt Nam thi đấu vòng loại World Cup khi nào?",
    "Triệu chứng của bệnh sốt xuất huyết là gì?",
    "Thủ tục đăng ký kết hôn với người nước ngoài gồm những gì?",
    "Học phí ngành Luật của Đại học Bách khoa Hà Nội là bao nhiêu?",
    "Tỷ giá USD/VND hôm nay là bao nhiêu?",
]


def best_dense_score(query: str) -> float:
    results = semantic_search(query, top_k=10)
    return float(results[0]["score"]) if results else 0.0


def summarize(label: str, scores: list[float]) -> dict:
    return {
        "label": label,
        "n": len(scores),
        "min": round(min(scores), 4),
        "p25": round(statistics.quantiles(scores, n=4)[0], 4),
        "median": round(statistics.median(scores), 4),
        "p75": round(statistics.quantiles(scores, n=4)[2], 4),
        "max": round(max(scores), 4),
        "mean": round(statistics.fmean(scores), 4),
    }


def main() -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    in_domain = [(item["question"], best_dense_score(item["question"])) for item in golden]
    out_domain = [(query, best_dense_score(query)) for query in OUT_OF_DOMAIN_QUERIES]

    in_scores = [score for _, score in in_domain]
    out_scores = [score for _, score in out_domain]
    gap_low, gap_high = max(out_scores), min(in_scores)
    suggested = round((gap_low + gap_high) / 2, 2) if gap_low < gap_high else None

    payload = {
        "in_domain": summarize("in-domain (golden dataset)", in_scores),
        "out_of_domain": summarize("out-of-domain", out_scores),
        "separation": {
            "max_out_of_domain": round(gap_low, 4),
            "min_in_domain": round(gap_high, 4),
            "separable": gap_low < gap_high,
            "suggested_threshold": suggested,
        },
        "per_query": {
            "in_domain": [{"query": q, "best_dense_score": round(s, 4)} for q, s in in_domain],
            "out_of_domain": [{"query": q, "best_dense_score": round(s, 4)} for q, s in out_domain],
        },
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["in_domain"], ensure_ascii=False))
    print(json.dumps(payload["out_of_domain"], ensure_ascii=False))
    print(json.dumps(payload["separation"], ensure_ascii=False))
    print(f"Saved -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
