import json
import re
from pathlib import Path

import ollama
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

# seuil minimum de caracteres par page pour considerer qu'elle contient du vrai texte
MIN_CHARS_PER_PAGE = 30

# prompt envoye a llama3 pour classifier le document
# {{ }} pour echapper les accolades avec .format()
VALIDATION_PROMPT = """
Analyse ce texte et réponds UNIQUEMENT en JSON.
Le document peut être en français, en arabe ou en anglais.

Format :
{{
  "is_cv": true ou false,
  "document_type": "CV / Facture / Rapport / Médical / Juridique / Autre",
  "reason": "explique en une phrase pourquoi c'est ce type de document, sans copier le texte"
}}

Texte :
{text}
"""


# nettoie la reponse du modele et la convertit en dict Python
# gere les cas ou le JSON est entoure de ```json ... ```
def _parse_json_response(content: str) -> dict:
    raw = re.sub(r"```json|```", "", content).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # fallback : chercher le JSON entre { } si le parsing direct echoue
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Réponse JSON invalide : {raw}")


# extrait le texte d'un PDF page par page
# bascule vers l'OCR si trop de pages semblent etre des images
def extract_text(pdf_path: str) -> dict:
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    # uniquement les fichiers PDF sont acceptes
    if path.suffix.lower() != ".pdf":
        raise ValueError(
            f"Format non supporté : '{path.suffix}' — seuls les PDFs sont acceptés"
        )

    pages = []
    image_pages = []

    try:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = (page.extract_text() or "").strip()
                pages.append(text)
                # page avec peu de texte = probablement une image
                if len(text) < MIN_CHARS_PER_PAGE:
                    image_pages.append(i + 1)
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la lecture du PDF : {e}") from e

    full_text = "\n\n".join(pages)
    total_pages = len(pages)

    # OCR necessaire si au moins la moitie des pages sont des images
    needs_ocr = len(image_pages) >= max(1, total_pages // 2)

    if needs_ocr:
        try:
            # convertir les pages en images puis extraire le texte via OCR
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


# envoie un extrait du texte a llama3 pour verifier si c'est bien un CV
def validate_document(extracted: dict) -> dict:
    # on envoie seulement les 1500 premiers caracteres, suffisant pour classifier
    sample = extracted["text"][:1500]

    try:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "user", "content": VALIDATION_PROMPT.format(text=sample)}
            ],
            # temperature basse pour une reponse stable et deterministe
            options={"temperature": 0.1},
        )
        return _parse_json_response(response["message"]["content"])
    except Exception as e:
        raise RuntimeError(f"Erreur lors de la validation du document : {e}") from e


def main():
    import sys

    # chemin du PDF depuis l'argument ou saisi par l'utilisateur
    pdf = sys.argv[1] if len(sys.argv) > 1 else input("Chemin du PDF : ")

    try:
        # etape 1 : extraction
        print("\nExtraction en cours...")
        result = extract_text(pdf)
        print(f"Fichier    : {result['file_name']}")
        print(f"Pages      : {result['num_pages']}")
        print(f"Caractères : {len(result['text'])}")
        print(f"Pages image: {result['image_pages']}")
        print(f"OCR requis : {result['needs_ocr']}")
        print("=" * 60)

        # etape 2 : validation
        print("Validation en cours...")
        validation = validate_document(result)
        print(f"Est un CV  : {validation['is_cv']}")
        print(f"Type doc   : {validation['document_type']}")
        print(f"Raison     : {validation['reason']}")
        print("=" * 60)

        # sauvegarder uniquement si c'est un CV
        if validation.get("is_cv"):
            raw_output_file = Path(pdf).stem + "_raw.txt"
            with open(raw_output_file, "w", encoding="utf-8") as f:
                f.write(result["text"])
            print(f"\n✅ Texte sauvegardé dans : {raw_output_file}")
        else:
            print(
                f"\n❌ Document rejeté — ce n'est pas un CV ({validation['document_type']})"
            )

    except Exception as e:
        print(f"\nErreur : {e}")


if __name__ == "__main__":
    main()
