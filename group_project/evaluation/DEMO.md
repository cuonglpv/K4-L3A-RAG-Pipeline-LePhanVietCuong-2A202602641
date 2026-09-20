# Demo transcript

Chạy lúc 2026-09-20 17:50:19 bằng `python -m group_project.evaluation.demo_queries`.

- Generator: `gemini-3.1-flash-lite` (provider `gemini`)
- Embedding: `BAAI/bge-m3`
- `SCORE_THRESHOLD`: `0.58`, `top_k` = 5
- Retrieval: hybrid (dense + BM25 + RRF) như cấu hình mặc định của chatbot

## Query 1 — trong domain

**Query:** Điều kiện CGPA để duy trì học bổng toàn phần là gì?

- Best dense cosine score: `0.6854`
- `retrieval_source`: `hybrid`
- Latency: 3.872s

**Answer:**

```text
Điều kiện để duy trì học bổng toàn phần là sinh viên cần đạt điểm trung bình (GPA) từ 3.2 trở lên [source:news/article_05.md::chunk-19].
```

**Nguồn được trả về (đúng những gì UI hiển thị):**

| # | Chunk ID | Title | Score | Method |
| --: | --- | --- | --: | --- |
| 1 | `legal/vinuni-scholarship-maintenance-2025.md::chunk-7` | vinuni-scholarship-maintenance-2025 | 0.0328 | hybrid |
| 2 | `legal/vinuni-scholarship-maintenance-2025.md::chunk-6` | vinuni-scholarship-maintenance-2025 | 0.0320 | hybrid |
| 3 | `legal/vinuni-scholarship-maintenance-2025.md::chunk-15` | vinuni-scholarship-maintenance-2025 | 0.0315 | hybrid |
| 4 | `news/article_05.md::chunk-19` | Tuition Fee, Scholarship, and Financial Aids - Admission | 0.0161 | hybrid |
| 5 | `legal/vinuni-scholarship-maintenance-2025.md::chunk-3` | vinuni-scholarship-maintenance-2025 | 0.0156 | hybrid |

## Query 2 — ngoài domain

**Query:** Cách nấu phở bò truyền thống ngon nhất là gì?

- Best dense cosine score: `0.3177`
- `retrieval_source`: `hybrid`
- Latency: 2.152s

**Answer:**

```text
Thông tin về cách nấu phở bò truyền thống không có trong các tài liệu được cung cấp. Do đó, tôi từ chối xác minh yêu cầu này.
```

**Nguồn được trả về (đúng những gì UI hiển thị):**

| # | Chunk ID | Title | Score | Method |
| --: | --- | --- | --: | --- |
| 1 | `legal/vinuni-financial-regulations-ay25-26.md::chunk-100` | vinuni-financial-regulations-ay25-26 | 0.0296 | hybrid |
| 2 | `legal/vinuni-financial-regulations-ay25-26.md::chunk-112` | vinuni-financial-regulations-ay25-26 | 0.0164 | hybrid |
| 3 | `legal/vinuni-financial-regulations-ay25-26.md::chunk-34` | vinuni-financial-regulations-ay25-26 | 0.0164 | hybrid |
| 4 | `legal/vinuni-financial-regulations-ay25-26.md::chunk-110` | vinuni-financial-regulations-ay25-26 | 0.0161 | hybrid |
| 5 | `legal/vinuni-financial-regulations-ay25-26.md::chunk-73` | vinuni-financial-regulations-ay25-26 | 0.0161 | hybrid |
