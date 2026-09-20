"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import re


CORPUS: list[dict] = []


def _tokenize(text: str) -> list[str]:
    """Tokenize consistently for both corpus documents and queries."""
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    return BM25Okapi([_tokenize(item["content"]) for item in corpus])


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    corpus = CORPUS or _load_chunk_corpus()
    if top_k <= 0 or not query.strip() or not corpus:
        return []

    bm25 = build_bm25_index(corpus)
    scored = zip(bm25.get_scores(_tokenize(query)), corpus)
    ranked = sorted(scored, key=lambda pair: float(pair[0]), reverse=True)
    return [
        {
            "id": item["id"],
            "content": item["content"],
            "score": float(score),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        }
        for score, item in ranked
    ][:top_k]


def _load_chunk_corpus() -> list[dict]:
    """Use the same standardized documents and chunking configuration as Task 4."""
    from .task4_chunking_indexing import chunk_documents, load_documents

    return chunk_documents(load_documents())


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
