"""
test_pymupdf.py — Extraction avec PyMuPDF
Usage: python tests\test_pymupdf.py mon_cv.pdf
"""

import sys
import fitz
from pathlib import Path


def extract(path):
    doc = fitz.open(path)
    pages = []
    for page in doc:
        blocks = page.get_text("blocks")
        text_blocks = [b for b in blocks if b[6] == 0 and str(b[4]).strip()]
        sorted_blocks = sorted(
            text_blocks, key=lambda b: (round(float(b[1]) / 10), float(b[0]))
        )
        pages.append("\n".join(str(b[4]).strip() for b in sorted_blocks))
    doc.close()
    return "\n\n".join(pages)


if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else input("PDF : ")
    path = Path(pdf)
    if not path.exists():
        print(f"Fichier introuvable : {pdf}")
        sys.exit(1)

    text = extract(str(path))
    print(f"Chars : {len(text)}")
    print("=" * 60)
    print(text)
