import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="VinUni Financial Support RAG",
    page_icon="🎓",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_sources(sources: list[dict], retrieval_source: str) -> None:
    """Render only the chunks returned by the retrieval pipeline."""
    if not sources:
        return
    with st.expander(f"Nguồn truy xuất ({retrieval_source})", expanded=False):
        for index, source in enumerate(sources, 1):
            metadata = source["metadata"]
            st.markdown(f"**[{index}] {metadata['title']}**")
            st.caption(
                f"{source['id']} · {source['retrieval_method']} · "
                f"score: {source['score']:.4f}"
            )
            if metadata.get("url"):
                st.markdown(f"[Mở nguồn gốc]({metadata['url']})")
            else:
                st.caption(f"Tệp corpus: {metadata['source']}")

with st.sidebar:
    st.title("VinUni RAG")
    st.caption("Học phí, học bổng và hỗ trợ tài chính bậc đại học")
    top_k = st.slider("Số chunks", 3, 10, 5)

st.title("Hỏi đáp chính sách tài chính VinUni")
st.caption("Câu trả lời chỉ dùng các nguồn đã được truy xuất từ corpus.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(
                message.get("sources", []), message.get("retrieval_source", "none")
            )

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        render_sources(result["sources"], result["retrieval_source"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "retrieval_source": result["retrieval_source"],
        }
    )
