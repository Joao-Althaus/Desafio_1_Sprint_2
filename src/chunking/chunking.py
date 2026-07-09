import argparse
import json
from pathlib import Path
import tiktoken
from collections import defaultdict
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm
import re
import hashlib

PROCESSED_DIR = Path("data/processed")
CHUNKED_DIR = Path("data/chunked")

def main(
    processed_dir: Path | None = PROCESSED_DIR,
    chunked_dir: Path | None = CHUNKED_DIR,
    output_file: Path | None = None,
) -> None:
    """processes the JSON file containing the processed data and generates chunks from it"""
    output_file = output_file or chunked_dir / "chunks.json"
    chunked_dir.mkdir(parents=True, exist_ok=True)

    processed_data = processed_dir / "documents.json"

    if not processed_data.exists():
        print(f"Nenhum dado encontrado em {processed_dir}.")
        return

    print("=" * 50)
    with open(processed_data, 'r', encoding='utf-8') as file:
        data = json.load(file)

    print(f"Processando dados de {processed_data} para gerar chunks...")
    ready_data = prepare_data_for_chunking(data)
    chunks = generate_chunks(ready_data)

    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(chunks, output, ensure_ascii=False, indent=2)

    print(f"{len(chunks)} chunks gerados com sucesso e salvos em {output_file}.")
    print("=" * 50)


def generate_chunks(documents: list[dict]) -> list[dict]:
    """
    It generates chunks based on the documents; after creating a chunk, 
    it identifies the page range from the tags associated with that chunk 
    to save as metadata, then removes the tags to clean the text, while also 
    saving a hash of the text within the chunk..
    """
    encoding = tiktoken.get_encoding("cl100k_base")

    # Create a text splitter with specified parameters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,      
        chunk_overlap=200,    
        length_function=lambda text: len(encoding.encode(text)),
        separators=["\n\n", "\n", ". ", "; ", ", ", " "],
    )

    final_chunks = []

    for doc_id, text in tqdm(documents.items(), desc="Fatiando Documentos (Chunking)", unit="doc"):

        raw_chunks = splitter.split_text(text)

        last_seen_page = 1

        for index, chunk in enumerate(raw_chunks):     

            # find all page numbers in the chunk using regex  
            pages_found = [int(x) for x in re.findall(r"\[PAGE (\d+)\]", chunk)]

            # if pages are found, set the page_start and page_end accordingly; otherwise, use the last seen page
            if pages_found:
                page_start = min(pages_found)
                page_end = max(pages_found)
                last_seen_page = page_end 
            else:
                page_start = last_seen_page
                page_end = last_seen_page

            clean_chunk_text = re.sub(r"\[PAGE \d+\]", "", chunk).strip()

            if not clean_chunk_text:
                continue

            # generate a hash for the cleaned chunk text
            chunk_hash = make_content_hash(clean_chunk_text)

            final_chunks.append({
                "id": f"{doc_id}_chunk_{index}",
                "text": clean_chunk_text,
                "content_hash": chunk_hash,
                "metadata": {
                    "document_id": doc_id,
                    "chunk_number": index,
                    "page_start": page_start,
                    "page_end": page_end,
                }
            })

    return final_chunks


def prepare_data_for_chunking(documents: list[dict]) -> list[dict]:
    """
    Prepares the data for segmentation by creating a string that 
    concatenates all pages within a document, adding tags containing page numbers to preserve context.
    """

    grouped_documents = defaultdict(list)

    # Group documents by their document_id
    for page in documents:
        doc_id = page.get("document_id")
        grouped_documents[doc_id].append(page)

    texts_ready_for_chunking = {}

    for doc_id, pages in grouped_documents.items():
        # Sort pages by page number to maintain order
        ordered_pages = sorted(pages, key=lambda x: x.get("page", 0))

        full_text = []
        
        for page in ordered_pages:
            page_number = page["page"]
            clean_text = page["text"]

            # Add a tag with the page number to preserve context
            full_text.append(f"[PAGE {page_number}]\n{clean_text}\n")
        
        # Create a single string for the entire document
        texts_ready_for_chunking[doc_id] = "".join(full_text)

    return texts_ready_for_chunking


def make_content_hash(text: str) -> str:
    """
    Generates a SHA-256 hash for the given text.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Processa o arquivo JSON contendo os dados processados e gera chunks a partir dele")
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR, help="Diretório para receber os dados processados")
    parser.add_argument("--chunked-dir", type=Path, default=CHUNKED_DIR, help="Diretório para salvar os chunks gerados")
    parser.add_argument("--output-file", type=Path, default=None, help="Caminho do arquivo JSON de saída")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(processed_dir=args.processed_dir, chunked_dir=args.chunked_dir, output_file=args.output_file)