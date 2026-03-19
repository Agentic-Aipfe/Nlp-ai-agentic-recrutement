import pdfplumber
import pytesseract
from pathlib import Path
from pdf2image import convert_from_path

MIN_CHARS_PER_PAGE = 30


def extract_text(pdf_path: str) -> dict:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    pages = []
    image_pages = []

    try:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = (page.extract_text() or "").strip()
                pages.append(text)
                if len(text) < MIN_CHARS_PER_PAGE:
                    image_pages.append(i + 1)
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la lecture du PDF : {e}") from e

    full_text = "\n\n".join(pages)
    total_pages = len(pages)
    needs_ocr = len(image_pages) >= max(1, total_pages // 2)

    if needs_ocr:
        try:
            images = convert_from_path(pdf_path)
            full_text = "\n\n".join(
                pytesseract.image_to_string(img, lang="fra+eng").strip()
                for img in images
            )
        except Exception as e:
            raise RuntimeError(f"Erreur lors de l'OCR du PDF : {e}") from e

    return {
        "text": full_text,
        "num_pages": total_pages,
        "file_name": path.name,
        "image_pages": image_pages,
        "needs_ocr": needs_ocr,
    }
