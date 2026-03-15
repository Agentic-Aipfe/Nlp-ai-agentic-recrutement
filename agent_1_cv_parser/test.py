"""test.py — Compare pdfplumber vs PyMuPDF extraction on the same CV."""

import sys
import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path

_MIN_CHARS = 30


def extract_with_pymupdf(pdf_path: str) -> dict:
    path = Path(pdf_path)
    pages = []
    image_pages = []

    with fitz.open(str(path)) as doc:
        for i, page in enumerate(doc):  # type: ignore
            text = page.get_text().strip()
            pages.append(text)
            if len(text) < _MIN_CHARS:
                image_pages.append(i + 1)

    return {
        "text": "\n\n".join(pages),
        "num_pages": len(pages),
        "image_pages": image_pages,
    }


def extract_with_pdfplumber(pdf_path: str) -> dict:
    path = Path(pdf_path)
    pages = []
    image_pages = []

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").strip()
            pages.append(text)
            if len(text) < _MIN_CHARS:
                image_pages.append(i + 1)

    return {
        "text": "\n\n".join(pages),
        "num_pages": len(pages),
        "image_pages": image_pages,
    }


def compare(pdf_path: str) -> None:
    path = Path(pdf_path)
    name = path.stem

    print(f"\n{'=' * 60}")
    print(f"  CV : {path.name}")
    print(f"{'=' * 60}")

    mupdf = extract_with_pymupdf(pdf_path)
    plumber = extract_with_pdfplumber(pdf_path)

    print(
        f"\n  PyMuPDF    → {len(mupdf['text'])} chars | "
        f"image pages: {mupdf['image_pages']}"
    )
    print(
        f"  pdfplumber → {len(plumber['text'])} chars | "
        f"image pages: {plumber['image_pages']}"
    )

    # Save to files for manual comparison
    out = Path("test_output")
    out.mkdir(exist_ok=True)

    (out / f"{name}_pymupdf.txt").write_text(mupdf["text"], encoding="utf-8")
    (out / f"{name}_pdfplumber.txt").write_text(plumber["text"], encoding="utf-8")

    print("\n  Saved to:")
    print(f"    test_output/{name}_pymupdf.txt")
    print(f"    test_output/{name}_pdfplumber.txt")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test.py cv1.pdf cv2.pdf cv3.pdf")
        sys.exit(1)

    for pdf in sys.argv[1:]:
        try:
            compare(pdf)
        except Exception as e:
            print(f"\n  ✗ {pdf} — {e}")

    print(f"\n{'=' * 60}")
    print("  Done. Compare the .txt files in test_output/")
    print(f"{'=' * 60}")
