import pdfplumber
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path

_MIN_CHARS_PER_PAGE = 30


def extract_text_from_pdf(pdf_file_path: str) -> dict:
    """Étape 1 — Extraction du texte.

    2-Chargement du fichier PDF
    3-Extraction du contenu textuel natif de chaque page
    4-Concaténation en corpus textuel unique

    Renvoie des données structurées afin que l'agent puisse déterminer
    le traitement approprié pour les pages de type image..
    """
    file_path = Path(pdf_file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    # 02 — Chargement  &  03 — Extraction par page
    pages = []
    image_pages = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = (page.extract_text() or "").strip()
            pages.append(text)

            # si la page contient très peu de texte, on la marque comme page image
            if len(text) < _MIN_CHARS_PER_PAGE:
                image_pages.append(i + 1)

    # 04 — Tentative de concaténation du texte natif
    full_text = "\n\n".join(pages)
    total_pages = len(pages)

    # si la moitié du document semble être composée d'images
    # on relance une extraction complète via OCR pour tout le document

    if len(image_pages) >= max(1, total_pages // 2):
        images = convert_from_path(pdf_file_path)
        full_text = ""
        for img in images:
            full_text += pytesseract.image_to_string(img, lang="fra+eng")

    # on retourne tout dans un dict clair pour un agent qui peut décider de faire du OCR ou pas selon les besoins
    return {
        "text": full_text,
        "pages": pages,
        "num_pages": total_pages,
        "file_name": file_path.name,
        "image_pages": image_pages,
        "is_scannable": len(image_pages) >= max(1, total_pages // 2),
        "needs_ocr": len(image_pages) >= max(1, total_pages // 2),
    }


if __name__ == "__main__":
    import sys

    # on récupère le chemin du PDF depuis l'argument du terminal
    # sinon on demande à l'utilisateur de le saisir
    pdf = sys.argv[1] if len(sys.argv) > 1 else input("Chemin du PDF : ")
    result = extract_text_from_pdf(pdf)

    print(f"Pages      : {result['num_pages']}")
    print(f"Caractères : {len(result['text'])}")
    print(f"Pages image: {result['image_pages']}")
    print(f"Scanné     : {result['is_scannable']}")
    print("=" * 60)
    print(result["text"])

    # sauvegarde du OUTPUT dans un fichier .txt (called name_raw)
    raw_output_file = Path(pdf).stem + "_raw.txt"
    with open(raw_output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    print(f"\nTexte sauvegardé dans : {raw_output_file}")
