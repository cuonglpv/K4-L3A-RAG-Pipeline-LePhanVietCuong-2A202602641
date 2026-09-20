# RAG evaluation results

Toàn bộ số liệu dưới đây được sinh từ `python -m group_project.evaluation.run_ab_eval`
(dữ liệu thô: `ab_results.json`, câu trả lời từng case: `ab_generations.json`,
phân bố score dùng để chọn threshold: `threshold_calibration.json`).

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | Ragas 0.4.3 |
| Evaluator model                    | `gemini-3.5-flash-lite` (giới hạn 13 RPM ở tầng client) |
| Generator model                    | `gemini-3.1-flash-lite`, temperature 0.3, top_p 0.9 |
| Embedding model                    | `BAAI/bge-m3` (1024 dimensions), dùng chung cho corpus, query và answer relevance |
| Corpus version/commit              | 314 chunks từ `data/standardized/` (3 legal + 5 news), chunk 500/overlap 50, trên commit `0a22c7a` |
| Golden dataset size                | 18 |
| `top_k`                            | 5 |
| Fallback threshold and calibration | Đang đặt `0.3`; đo được cho thấy nên đặt **0.58** (xem mục “Hiệu chỉnh threshold”) |

Generator không phải `gemini-2.5-flash` như `.env` mặc định vì free tier của key
chỉ cho 20 request/ngày với model đó, không đủ cho 36 lần generate của A/B.
Generator và evaluator là hai model khác nhau nên evaluator không chấm chính đầu ra của mình.

## Configurations

- **Config A — dense-only:** `retrieve(..., use_reranking=False)`, lấy top-5 từ dense search; fallback và generation giữ nguyên như Config B.
- **Config B — hybrid + RRF:** dense top-10 + BM25 top-10, RRF với `k=60`, lấy top-5; fallback và generation giữ nguyên như Config A.

Hai config dùng chung golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |   0.9889 |   0.9518 |   −0.0371 |
| Answer relevance  |   0.8614 |   0.7988 |   −0.0626 |
| Context recall    |   0.7778 |   0.7222 |   −0.0556 |
| Context precision |   0.6132 |   0.4873 |   −0.1259 |
| **Average**       |   0.8103 |   0.7400 |   −0.0703 |

18/18 case được chấm ở cả hai cấu hình, không có case nào lỗi hoặc thiếu điểm.

## A/B comparison

**Cấu hình tốt hơn: Config A (dense-only).** Trên corpus này hybrid + RRF thua ở cả bốn metric.

Evidence:

| Chỉ số quan sát được | Config A | Config B |
| --- | --: | --: |
| Case có đúng tài liệu nguồn (golden `source`) trong top-5 | 16/18 | 11/18 |
| Tổng số chunk từ `news/` lọt vào top-5 (18 case × 5) | 30 | 17 |
| Case tốt hơn cấu hình còn lại | 10 | 7 (1 hoà) |
| Safe refusal **sai** (evidence có trong corpus nhưng vẫn từ chối) | 0 | 1 |
| Safe refusal **đúng** (evidence không có trong corpus) | 1 | 1 |

Nguyên nhân: corpus lệch rất mạnh về một tài liệu dài
(`vinuni-financial-regulations-ay25-26.md` chiếm phần lớn trong 314 chunks). BM25 xếp
hạng cao các chunk của tài liệu này vì trùng từ khoá tiếng Việt thông dụng
(“học phí”, “sinh viên”, “hỗ trợ”), và vì RRF chỉ cộng nghịch đảo thứ hạng nên một chunk
xuất hiện ở hạng trung bình trong *cả hai* danh sách vẫn đẩy được chunk mà dense xếp hạng
đầu ra khỏi top-5. Kết quả là các chunk `news/` mang evidence bị loại, kéo context
precision xuống nhiều nhất (−0.126).

Trade-off latency/cost: retrieval p50 0.197s (A) so với 0.193s (B), p95 0.216s so với
0.245s — chênh lệch không đáng kể vì BM25 chạy trên corpus nhỏ trong bộ nhớ. End-to-end
p50 5.489s (A) so với 6.101s (B), p95 7.582s so với 8.078s; phần lớn thời gian là gọi LLM.
Chi phí generation và evaluation bằng nhau giữa hai cấu hình (cùng model, cùng `top_k`,
cùng prompt). Nói cách khác Config B đắt hơn một chút mà điểm thấp hơn, nên không có lý do
giữ nó ở cấu hình hiện tại.

## Hiệu chỉnh threshold

`python -m group_project.evaluation.calibrate_threshold` đo best dense cosine score trên
18 query in-domain và 8 query out-of-domain:

| Nhóm query | min | p25 | median | p75 | max |
| --- | --: | --: | --: | --: | --: |
| In-domain (golden dataset) | 0.5927 | 0.6499 | 0.6710 | 0.7119 | 0.7615 |
| Out-of-domain | 0.3177 | 0.3757 | 0.4257 | 0.5518 | 0.6045 |

Hai phân bố chồng nhau ở đúng một query (“Tỷ giá USD/VND hôm nay là bao nhiêu?”, score
0.6045, khớp nhầm với các chunk nói về tài khoản VND). Ngưỡng **0.58** giữ được 18/18 query
in-domain và loại 7/8 query out-of-domain, nên tốt hơn hẳn giá trị `0.3` đang đặt trong
`.env` — ở mức 0.3 thì không query out-of-domain nào bị chặn.

Lưu ý: PageIndex fallback chưa được triển khai (`task8_pageindex_vectorless.py` còn
`NotImplementedError`), nên khi score dưới ngưỡng, `retrieve()` bắt exception và trả lại
hybrid results. Phòng tuyến thực tế cho query ngoài domain hiện nay là safe refusal ở
tầng generation, đã kiểm chứng trong `DEMO.md`.

## Worst performers

Ba case điểm thấp nhất (trung bình bốn metric của Config A, cấu hình được chọn):

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
|   1 | Nếu hồ sơ hỗ trợ tài chính chưa đầy đủ thì được báo trong bao lâu? | A | 1.00 | 0.00 | 0.00 | 0.00 | Data / golden dataset | Corpus chuẩn hoá **không chứa** mốc “3 ngày làm việc” cho hồ sơ thiếu; chỉ có một câu “3 ngày làm việc” về đăng ký dịch vụ, không liên quan. Hệ thống từ chối đúng (faithfulness 1.0) nhưng bị chấm 0 ở ba metric còn lại. Đây là lỗi golden case không grounded, không phải lỗi retrieval. |
|   2 | Sinh viên hiện tại cần điều kiện chung nào để được hỗ trợ tài chính? | A | 1.00 | 0.96 | 0.00 | 0.00 | Retrieval | Top-5 lấy chunk về *duy trì* học bổng (`vinuni-scholarship-maintenance-2025.md`) thay vì mục “Eligibility Criteria” của `vinuni-financial-support-guidelines-2024.md`. Câu hỏi chung chung, nhiều chunk cùng nói về “điều kiện” nên dense không tách được mục đúng. |
|   3 | Khi nào có thể bị tính học phí theo tín chỉ? | A | 1.00 | 0.95 | 0.00 | 0.25 | Retrieval (sai tài liệu nguồn) | Evidence mong đợi nằm ở `article_01.md` nhưng top-5 toàn chunk của quy chế tài chính; câu trả lời vẫn đúng và có citation, tuy nhiên recall tính theo golden context nên bằng 0. Golden context viết bằng tiếng Anh trong khi chunk tương ứng là bảng tiếng Việt. |

Hai case tụt điểm nặng nhất khi chuyển sang Config B (bằng chứng trực tiếp cho kết luận A/B):

| Question | Avg A | Avg B | Điều gì đã xảy ra |
| --- | --: | --: | --- |
| Tiền hỗ trợ học phí và hỗ trợ ngoài học phí được giải ngân khác nhau thế nào? | 0.845 | 0.125 | Chunk chứa evidence (`vinuni-financial-support-guidelines-2024.md::chunk-14`) đứng hạng 2 ở A nhưng bị BM25 + RRF đẩy khỏi top-5 ở B; B trả safe refusal dù corpus có câu trả lời. |
| Phí ký túc xá tham khảo cho sinh viên năm nhất là bao nhiêu? | 0.798 | 0.423 | `news/article_04.md::chunk-14` (15.000.000 VND/học kỳ) ở hạng 5 tại A, biến mất ở B; B trả lời bằng bảng giá ký túc xá theo tháng của quy chế — đúng nguồn nhưng sai câu hỏi. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
| 1 | Giữ hybrid + RRF trong sản phẩm (đề bài yêu cầu dense + BM25 + RRF) nhưng chuyển sang weighted RRF ưu tiên dense thay vì cộng đều hai danh sách; nếu chỉ xét điểm thì dense-only đang tốt hơn | Config B thua cả bốn metric; số case có đúng tài liệu nguồn trong top-5 giảm 16→11 | Lấy lại ~0.07 điểm trung bình, +0.13 context precision | Chạy lại `run_ab_eval.py` với cấu hình mới, so sánh trên đúng 18 case này |
| 2 | Cân bằng ảnh hưởng của BM25: bỏ stopword tiếng Việt khi tokenize và/hoặc chuẩn hoá theo độ dài tài liệu, vì một tài liệu dài đang chiếm phần lớn corpus | 30→17 chunk `news/` lọt top-5 khi bật BM25; các chunk bị loại chính là chunk mang evidence | Giữ recall của hybrid mà không mất chunk hiếm | A/B lại chỉ đổi tokenizer, giữ nguyên mọi tham số khác |
| 3 | Sửa `SCORE_THRESHOLD` từ `0.3` thành `0.58` trong `.env` và triển khai PageIndex fallback | Phân bố score in-domain (min 0.5927) và out-of-domain (max 0.6045) tách nhau ở 0.58; mức 0.3 không chặn được query nào | Query ngoài domain bị chặn ở tầng retrieval thay vì phụ thuộc hoàn toàn vào prompt | Chạy lại `calibrate_threshold.py` sau khi đổi corpus, và kiểm tra `DEMO.md` query 2 |
| 4 | Rà lại 3 golden case không grounded hoặc lệch ngôn ngữ (case #1, #3 ở bảng trên) | Evidence không tồn tại trong corpus chuẩn hoá, hoặc golden context tiếng Anh trong khi chunk là tiếng Việt | Bỏ nhiễu khỏi context recall; điểm phản ánh đúng chất lượng retrieval | Sau khi sửa dataset, chạy lại A/B và so recall trước/sau |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Chưa thực hiện (HyDE, reranker nâng cao, conversation memory, deploy) | RRF baseline | — | — | Không tuyên bố bonus khi chưa có phép đo |
