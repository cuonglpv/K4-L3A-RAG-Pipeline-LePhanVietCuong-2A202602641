# Thành viên nhóm K4-L3A

Dự án: RAG pipeline hỏi đáp chính sách học phí, học bổng và hỗ trợ tài chính VinUni.
Repository: `K4-L3A-RAG-Pipeline-LePhanVietCuong-2A202602641` (branch `main`).

| Họ và tên | Mã học viên | Vai trò chính | Deliverable trực tiếp phụ trách | Báo cáo cá nhân |
| --- | --- | --- | --- | --- |
| Nguyễn Đức Danh | 2A202602722 | Data & evaluation dataset | Thu thập 3 tài liệu pháp lý + 5 bài viết, chuẩn hoá Markdown, xây 18 golden case | [K4-L3A-2A202602722-NguyenDucDanh.md](reports/K4-L3A-2A202602722-NguyenDucDanh.md) |
| Bùi Gia Chính | 2A202602693 | Indexing & retrieval | Chunking, embedding, Chroma index, dense search, BM25, RRF fusion | [K4-L3A-2A202602693-BuiGiaChinh.md](reports/K4-L3A-2A202602693-BuiGiaChinh.md) |
| Lê Phan Việt Cường | 2A202602641 | Pipeline, generation & UI | Retrieval pipeline + fallback, generation có citation, Streamlit app, báo cáo A/B | [K4-L3A-2A202602641-LePhanVietCuong.md](reports/K4-L3A-2A202602641-LePhanVietCuong.md) |

## Phân chia theo module

| Module | File | Owner |
| --- | --- | --- |
| Thu thập tài liệu pháp lý | [src/task1_collect_legal_docs.py](src/task1_collect_legal_docs.py) | Nguyễn Đức Danh |
| Crawl bài viết | [src/task2_crawl_news.py](src/task2_crawl_news.py) | Nguyễn Đức Danh |
| Chuẩn hoá Markdown | [src/task3_convert_markdown.py](src/task3_convert_markdown.py) | Nguyễn Đức Danh |
| Chunking, embedding, indexing | [src/task4_chunking_indexing.py](src/task4_chunking_indexing.py) | Bùi Gia Chính |
| Semantic search | [src/task5_semantic_search.py](src/task5_semantic_search.py) | Bùi Gia Chính |
| Lexical search (BM25) | [src/task6_lexical_search.py](src/task6_lexical_search.py) | Bùi Gia Chính |
| Reciprocal Rank Fusion | [src/task7_reranking.py](src/task7_reranking.py) | Bùi Gia Chính |
| PageIndex fallback | [src/task8_pageindex_vectorless.py](src/task8_pageindex_vectorless.py) | Lê Phan Việt Cường |
| Retrieval pipeline + fallback | [src/task9_retrieval_pipeline.py](src/task9_retrieval_pipeline.py) | Lê Phan Việt Cường |
| Generation có citation | [src/task10_generation.py](src/task10_generation.py) | Lê Phan Việt Cường |
| Chatbot Streamlit | [app.py](app.py) | Lê Phan Việt Cường |
| Golden dataset | [group_project/evaluation/golden_dataset.json](group_project/evaluation/golden_dataset.json) | Nguyễn Đức Danh |
| Báo cáo đánh giá A/B | [group_project/evaluation/RESULT.md](group_project/evaluation/RESULT.md) | Lê Phan Việt Cường (chạy đo), cả nhóm review |

Mỗi thành viên tự chịu trách nhiệm giải thích và chạy lại phần việc của mình trong buổi demo.
