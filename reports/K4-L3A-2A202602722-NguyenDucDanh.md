# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Đức Danh
- Mã học viên: 2A202602722
- Nhóm: K4-L3A
- Repository/branch: `nguyen-duc-danh`, baseline commit `6a2a2d4`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
| --- | --- | --- | --- |
| Thu thập corpus pháp lý | Chuẩn bị 3 tài liệu chính sách về học phí, hỗ trợ tài chính và duy trì học bổng. | `data/landing/legal/*.pdf` | Done |
| Thu thập nội dung web | Chuẩn bị 5 bài viết có metadata URL, tiêu đề, thời điểm crawl và Markdown. | `data/landing/news/article_01.json` đến `article_05.json` | Done |
| Chuẩn hoá và golden dataset | Đối chiếu Markdown chuẩn hoá và xây 18 câu hỏi có expected answer/context. | `data/standardized/**`, `group_project/evaluation/golden_dataset.json`, `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, `src/task3_convert_markdown.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Giữ riêng landing data và standardized Markdown.  
   **Lý do/evidence:** Tách nguồn gốc PDF/JSON khỏi dữ liệu đầu vào của chunking giúp provenance truy vết được; acceptance test kiểm tra cả hai loại dữ liệu.  
   **Trade-off:** Có thêm bước convert trước khi index.

2. **Quyết định:** Golden dataset gồm 18 case thay vì mức tối thiểu 15.  
   **Lý do/evidence:** `golden_dataset.json` có câu hỏi keyword, semantic và confusable, bao phủ học phí, học bổng và hỗ trợ tài chính.  
   **Trade-off:** Tốn thêm thời gian review ground truth và chạy evaluation.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_acceptance.py -q`.
- Kết quả: 5 passed; xác nhận 3 legal documents, 5 news JSON, Markdown chuẩn hoá cho hai nguồn, 18 golden cases và cấu trúc `RESULT.md`.
- Lỗi đã phát hiện và cách xử lý: loại cache/cấu hình cục bộ khỏi Git qua `.gitignore`; giữ `.env` cục bộ để chạy nhưng không commit.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Corpus hiện tập trung vào chính sách tài chính VinUni, chưa mở rộng sang các domain khác.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: bổ sung case khó về điều kiện ngoại lệ và kiểm chứng định kỳ URL nguồn.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Nguyễn Đức Danh
