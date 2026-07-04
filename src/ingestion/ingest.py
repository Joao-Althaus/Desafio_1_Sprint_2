import argparse
import json
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from tqdm import tqdm

from src.preprocessing.clean_text import clean_text

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "documents.json"


def main(
    raw_dir: Path | None = None,
    processed_dir: Path | None = None,
    output_file: Path | None = None,
) -> None:
    """Process PDF files from a raw directory and write normalized documents to JSON."""
    raw_dir = raw_dir or RAW_DIR
    processed_dir = processed_dir or PROCESSED_DIR
    output_file = output_file or processed_dir / "documents.json"

    processed_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(raw_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"Nenhum PDF encontrado em {raw_dir}.")
        return

    documents = []

    for pdf_path in tqdm(pdf_files, desc="Processando PDFs"):
        documents.extend(load_pdf_pages(pdf_path))

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(documents, file, ensure_ascii=False, indent=2)

    print("Ingestão Concluída!")
    print(f"PDFs processados: {len(pdf_files)}")
    print(f"Páginas processadas: {len(documents)}")
    print(f"Arquivo gerado: {output_file}")

def get_document_category(file_name: str) -> str:
    """
    Extracts the document category from the file name.
    Assumes the category is the first part of the file name before an underscore.
    """
    name = file_name.lower()
    if "bula" in name:
        return "Bula do Profissional"

    if "hipert" in name:
        return "PCDT Hipertensão Arterial"
    return "Documento Clínico"

def normalize_document_id(file_name: str) -> str:
    """
    Normalizes the document ID by removing the file extension and replacing spaces with underscores.
    """
    return (
        Path(file_name)
        .stem
        .lower()
        .replace(" ", "_")
        .replace("-", "_")

    )

def load_pdf_pages(pdf_path: Path) -> list[dict]:

    """
    Loads the pages of a PDF file and returns them as a list of strings.
    """
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()

    normalized_pages = []

    for page in pages:
        page_number = page.metadata.get("page", 0) + 1
        raw_text = page.page_content
        cleaned_text = clean_text(raw_text)

        if cleaned_text:
            normalized_pages.append(
                {
                    "document_id": normalize_document_id(pdf_path.name),
                    "document_name": pdf_path.stem,
                    "source_file": pdf_path.name,
                    "category": get_document_category(pdf_path.name),
                    "page": page_number,
                    "text": cleaned_text,
                }
            )
    return normalized_pages

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Processa PDFs e gera documentos JSON")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="Diretório com os PDFs de entrada")
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR, help="Diretório para salvar a saída")
    parser.add_argument("--output-file", type=Path, default=None, help="Caminho do arquivo JSON de saída")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(raw_dir=args.raw_dir, processed_dir=args.processed_dir, output_file=args.output_file)