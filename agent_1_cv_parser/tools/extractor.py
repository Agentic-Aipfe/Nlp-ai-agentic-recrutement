import pdfplumber
from pathlib import Path

_MIN_CHARS_PER_PAGE = 30


def extract_text_from_pdf(pdf_path: str) -> dict:
    """Étape 1 — Extraction du texte.

    02: Chargement du fichier PDF
    03: Extraction du contenu textuel natif de chaque page
    04: Concaténation en corpus textuel unique

    Returns structured data so the agent can decide
    how to handle image-based pages.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    # 02 — Chargement  &  03 — Extraction par page
    pages = []
    image_pages = []

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").strip()
            pages.append(text)

            if len(text) < _MIN_CHARS_PER_PAGE:
                image_pages.append(i + 1)

    # 04 — Concaténation
    corpus = "\n\n".join(pages)
    total = len(pages)

    return {
        "text": corpus,
        "pages": pages,
        "num_pages": total,
        "file_name": path.name,
        "image_pages": image_pages,
        "is_scannable": len(image_pages) >= max(1, total // 2),
    }


if __name__ == "__main__":
    import sys

    pdf = sys.argv[1] if len(sys.argv) > 1 else input("Chemin du PDF : ")
    result = extract_text_from_pdf(pdf)

    print(f"Pages      : {result['num_pages']}")
    print(f"Caractères : {len(result['text'])}")
    print(f"Pages image: {result['image_pages']}")
    print(f"Scanné     : {result['is_scannable']}")
    print("=" * 60)
    print(result["text"])
