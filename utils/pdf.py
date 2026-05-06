"""
utils/pdf.py
------------
Extract plain text from a PDF file using pypdf.

Usage:
    from utils.pdf import extract_text_from_pdf
    text = extract_text_from_pdf("lecture.pdf")
"""

from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF, page by page.

    Args:
        file_path: Path to the .pdf file

    Returns:
        Single string with all pages joined together

    Raises:
        FileNotFoundError: if the file doesn't exist
        ValueError: if no text could be extracted (scanned/image PDF)
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {file_path}")

    reader = PdfReader(str(path))
    pages_text = []

    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
            if text:
                pages_text.append(f"[Page {i + 1}]\n{text}")
        except Exception as e:
            print(f"  Warning: could not read page {i + 1}: {e}")

    if not pages_text:
        raise ValueError(
            "No extractable text found in this PDF.\n"
            "If it's a scanned document, it needs OCR first."
        )

    return "\n\n".join(pages_text)