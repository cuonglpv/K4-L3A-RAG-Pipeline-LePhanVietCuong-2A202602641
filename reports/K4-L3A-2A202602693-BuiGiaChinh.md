# Individual contribution report

## Thông tin

- Họ và tên: Bùi Gia Chính
- Mã học viên: 2A202602693
- Nhóm: K4-L3A
- Repository/branch: `main`, baseline commit `6a2a2d4`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
| --- | --- | --- | --- |
| Chunking và vector index | Cài đặt đọc Markdown, metadata provenance, recursive chunking, embedding và Chroma upsert. | `src/task4_chunking_indexing.py` | Done |
| Dense và lexical retrieval | Cài đặt semantic search dùng embedding chung và BM25 trên cùng corpus chunks. | `src/task5_semantic_search.py`, `src/task6_lexical_search.py` | Done |
| Hybrid fusion | Cài đặt Reciprocal Rank Fusion, deduplicate ID và đánh dấu output `hybrid`. | `src/task7_reranking.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng ID chunk ổn định theo `<document>::chunk-<index>`.  
   **Lý do/evidence:** `chunk_documents()` giữ source/title/doc_type/chunk_index và contract test kiểm uniqueness.  
   **Trade-off:** Thay đổi chunking configuration sẽ đổi ID và yêu cầu re-index.

2. **Quyết định:** Chuyển cosine distance của Chroma thành similarity, còn BM25 giữ điểm lexical riêng; RRF chỉ hợp nhất thứ hạng.  
   **Lý do/evidence:** `semantic_search()` trả `1 - distance`; `rerank_rrf()` deduplicate theo rank.  
   **Trade-off:** Score giữa dense/BM25/RRF không được so sánh trực tiếp.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py -q`.
- Kết quả: 15 passed; gồm kiểm tra schema, thứ tự score, uniqueness, shared embedding, BM25 và RRF.
- Lỗi đã phát hiện và cách xử lý: không đưa URL `None` vào Chroma metadata vì backend không persist null; adapter semantic khôi phục `url: None` trước khi trả public contract.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Model `BAAI/bge-m3` phải có sẵn hoặc được tải trước khi index/demo lần đầu.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: cache model và thêm hướng dẫn/offline check để demo lặp lại ổn định hơn.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: Bùi Gia Chính
