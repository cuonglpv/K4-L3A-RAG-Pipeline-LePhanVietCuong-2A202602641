# Individual contribution report

## Thông tin

- Họ và tên: Lê Phan Việt Cường
- Mã học viên: 2A202602641
- Nhóm: K4-L3A
- Repository/branch: `main`, baseline commit `6a2a2d4`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
| --- | --- | --- | --- |
| Retrieval orchestration | Ghép dense + BM25 bằng RRF, dùng dense cosine score để quyết định fallback và xử lý lỗi fallback an toàn. | `src/task9_retrieval_pipeline.py`, `src/task8_pageindex_vectorless.py` | Done / fallback provider pending |
| Generation có citation | Tạo context có title/source/chunk ID, gọi provider theo `.env` và safe refusal khi thiếu evidence/lỗi provider. | `src/task10_generation.py` | Done |
| Chatbot và evaluation handoff | Tạo giao diện Streamlit hiển thị answer và danh sách nguồn; chuẩn bị A/B protocol và phân tích failure. | `app.py`, `group_project/evaluation/RESULT.md` | Partial |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Ngưỡng fallback chỉ so sánh dense cosine score, không so sánh RRF score.  
   **Lý do/evidence:** `retrieve()` lưu `best_dense_score` trước RRF; contract test xác nhận fallback và việc RRF chỉ chạy một lần.  
   **Trade-off:** Cần calibrate `SCORE_THRESHOLD` bằng query in-domain/out-of-domain.

2. **Quyết định:** Khi provider generation, index hoặc PageIndex lỗi, trả safe refusal/hybrid result thay vì làm hỏng UI.  
   **Lý do/evidence:** `generate_with_citation()` bọc lỗi và `retrieve()` giữ hybrid results nếu fallback lỗi.  
   **Trade-off:** Người dùng nhận thông báo từ chối thay vì một câu trả lời suy đoán.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest -q -p no:cacheprovider`.
- Kết quả: 20 passed; bao gồm fallback, citation context, safe refusal và toàn bộ acceptance suite.
- Lỗi đã phát hiện và cách xử lý: PageIndex chưa được cấu hình nên được cô lập thành fallback; pipeline vẫn trả hybrid result nếu provider lỗi.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: chưa có phép đo A/B thực tế trong `RESULT.md` và PageIndex provider chưa được triển khai/kết nối.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: chạy đầy đủ 18 case ở hai cấu hình cùng model/prompt, ghi 4 metrics và latency rồi hoàn thiện A/B.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Lê Phan Việt Cường
