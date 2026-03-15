import sys
import pdfplumber
from pathlib import Path


def extract(path):
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text.strip())
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
