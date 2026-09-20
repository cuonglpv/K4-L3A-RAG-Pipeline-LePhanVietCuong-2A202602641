"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation theo đúng dạng [source:<chunk-id>] lấy từ context.
Nếu thiếu evidence, hãy từ chối xác minh. Không được tạo citation hoặc URL không có trong context."""

SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context."""
    if len(chunks) <= 2:
        return list(chunks)
    return chunks[::2] + chunks[1::2][::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        parts.append(
            f"[Document {index} | ID: {chunk['id']} | "
            f"Title: {metadata['title']} | Source: {metadata['source']}]\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    if not LLM_MODEL:
        raise ValueError("Set LLM_MODEL in .env before generating an answer")

    if LLM_PROVIDER == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model=LLM_MODEL,
            instructions=system_prompt,
            input=user_message,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.output_text.strip()

    if LLM_PROVIDER == "gemini":
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            ),
        )
        return (response.text or "").strip()

    if LLM_PROVIDER == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=1024,
            temperature=TEMPERATURE,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    if not query.strip() or top_k <= 0:
        return _safe_refusal()

    try:
        chunks = retrieve(query, top_k=top_k)
    except Exception:
        return _safe_refusal()
    if not chunks:
        return _safe_refusal()

    context = format_context(reorder_for_llm(chunks))
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception:
        # API configuration and provider outages must not bring down the chat UI.
        return _safe_refusal()
    if not answer:
        return _safe_refusal()

    retrieval_method = chunks[0]["retrieval_method"]
    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": (
            retrieval_method if retrieval_method in {"hybrid", "pageindex"} else "hybrid"
        ),
    }


def _safe_refusal() -> dict:
    return {
        "answer": SAFE_REFUSAL,
        "sources": [],
        "retrieval_source": "none",
    }


if __name__ == "__main__":
    print(generate_with_citation("test query"))
