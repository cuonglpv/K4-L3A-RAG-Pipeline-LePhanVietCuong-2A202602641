"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

from pathlib import Path
import json


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert every policy file to one deterministic Markdown output."""
    from markitdown import MarkItDown
    from .task1_collect_legal_docs import POLICY_SOURCES

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue
        content = converter.convert(str(path)).text_content.strip()
        if not content:
            raise ValueError(f"Conversion produced no content: {path}")
        source_url = POLICY_SOURCES.get(path.name)
        provenance = f"**Source:** {source_url}\n\n" if source_url else ""
        (output_dir / f"{path.stem}.md").write_text(
            provenance + content + "\n", encoding="utf-8"
        )


def convert_news_articles() -> None:
    """Convert article JSON to Markdown while retaining source provenance."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    required = {"url", "title", "date_crawled", "content_markdown"}
    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = required - data.keys()
        if missing:
            raise ValueError(f"{path} is missing metadata: {sorted(missing)}")
        content = str(data["content_markdown"]).strip()
        if not content:
            raise ValueError(f"Article is empty: {path}")
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        (output_dir / f"{path.stem}.md").write_text(
            header + content + "\n", encoding="utf-8"
        )


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
