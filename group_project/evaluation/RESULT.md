# RAG evaluation results

> **Trạng thái:** Chưa chạy A/B vì môi trường và corpus chưa được tạo xong.
> Các giá trị metric bên dưới được để trống có chủ đích; không có số liệu giả.

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | Chưa chạy; báo cáo chuẩn bị ngày 2026-09-20 |
| Framework and version              | Ragas 0.4.3 (theo `pyproject.toml`) |
| Evaluator model                    | Chưa cấu hình |
| Generator model                    | Đọc từ `LLM_MODEL`; chưa cấu hình |
| Embedding model                    | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dimensions) |
| Corpus version/commit              | Working tree trên commit `6a2a2d4`; phải thay bằng commit corpus khi chạy |
| Golden dataset size                | 18 |
| `top_k`                            | 5 |
| Fallback threshold and calibration | Tạm thời 0.3; phải hiệu chỉnh bằng query in-domain/out-of-domain trước khi chạy chính thức |

## Configurations

- **Config A — dense-only:** `retrieve(..., use_reranking=False)`, lấy top-5 dense; fallback và generation giữ nguyên như Config B.
- **Config B — hybrid + RRF:** dense top-10 + BM25 top-10, RRF với `k=60`, lấy top-5; fallback và generation giữ nguyên như Config A.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |        — |        — |         — |
| Answer relevance  |        — |        — |         — |
| Context recall    |        — |        — |         — |
| Context precision |        — |        — |         — |
| **Average**       |        — |        — |         — |

Ký hiệu `—` nghĩa là chưa đo, không phải điểm 0.

## A/B comparison

- Cấu hình tốt hơn: Chưa kết luận trước khi có đủ 18 kết quả cho cả hai cấu hình.
- Evidence: Sẽ dựa trên bốn metric, log retrieved chunk theo từng case và kiểm tra thủ công ba case kém nhất.
- Trade-off về latency/cost: Config B chạy thêm BM25 và RRF; cần ghi p50/p95 latency thực tế. Chi phí generation/evaluator phải giữ như nhau giữa hai cấu hình.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Chưa xác định trước khi chạy | — | — | — | — | — | Chưa phân loại | Chưa có evidence |
|   2 | Chưa xác định trước khi chạy | — | — | — | — | — | Chưa phân loại | Chưa có evidence |
|   3 | Chưa xác định trước khi chạy | — | — | — | — | — | Chưa phân loại | Chưa có evidence |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Nếu recall thấp: kiểm tra lại source/chunk và thử thay đổi overlap hoặc `top_k` | Case có claim trong golden context nhưng không xuất hiện trong retrieved chunks | Tăng context recall | Chạy lại đúng case với cùng generator/evaluator và so sánh recall trước/sau |
|        2 | Nếu precision của hybrid thấp: rà tokenization BM25 và `k` của RRF | Case có nhiều chunk nhiễu đứng trên chunk chứa evidence | Tăng context precision mà không giảm recall | A/B lại trên toàn bộ 18 case, chỉ thay một tham số mỗi lần |
|        3 | Nếu faithfulness thấp dù context đúng: siết prompt citation và safe refusal | Answer chứa claim không được retrieved context hỗ trợ | Tăng faithfulness | Kiểm tra claim-level citation và chạy lại cùng retrieved contexts |

Các dòng trên là kế hoạch phân tích được đăng ký trước, chưa phải kết luận cuối cùng.

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Chưa thực hiện | RRF baseline | — | — | Không tuyên bố bonus khi chưa có phép đo |
