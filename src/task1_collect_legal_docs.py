"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

POLICY_SOURCES = {
    "vinuni-financial-regulations-ay25-26.pdf": (
        "https://policy.vinuni.edu.vn/wp-content/uploads/2025/10/"
        "VU_TS03.VN_Quy-dinh-tai-chinh-va-Bieu-phi_AY25-26_20251008-Websent.pdf"
    ),
    "vinuni-scholarship-maintenance-2025.pdf": (
        "https://policy.vinuni.edu.vn/wp-content/uploads/2025/09/"
        "GDL-SAM-004-V2.1_Tieu-chi-duy-tri-Hoc-bong-dau-vao-va-"
        "Ho-tro-tai-chinh_4.9.2025.pdf"
    ),
    "vinuni-financial-support-guidelines-2024.pdf": (
        "https://policy.vinuni.edu.vn/wp-content/uploads/2024/09/"
        "VUNI.84_Guideline-for-Student-Financial-Support-Request_17.09.2024.pdf"
    ),
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    setup_directory()
    for filename, url in POLICY_SOURCES.items():
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        if len(response.content) <= 1024:
            raise ValueError(f"Downloaded file is unexpectedly small: {url}")
        output = DATA_DIR / filename
        output.write_bytes(response.content)
        print(f"Saved: {output}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
