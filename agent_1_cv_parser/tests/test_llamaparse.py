import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from llama_parse import LlamaParse

load_dotenv()


def extract(path):
    parser = LlamaParse(
        api_key=os.getenv("LLAMA_CLOUD_API_KEY"), result_type="markdown" # type: ignore
    )
    documents = parser.load_data(path)
    return "\n\n".join([doc.text for doc in documents])


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
