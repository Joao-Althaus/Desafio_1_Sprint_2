import argparse
import json
from pathlib import Path

from tqdm import tqdm

from src.embeddings.embedding_model import load_embedding_model

CHUNK_DIR = Path("data/chunked")
OUTPUT_DIR = Path("data/embeddings")

INPUT_FILE = CHUNK_DIR / "chunks.json"
OUTPUT_FILE = OUTPUT_DIR / "embeddings.json"


def main(
    input_file: Path | None = None,
    output_dir: Path | None = None,
    output_file: Path | None = None,
    model_name: str | None = None,
):

    input_file = input_file or INPUT_FILE
    output_dir = output_dir or OUTPUT_DIR
    output_file = output_file or OUTPUT_FILE

    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_file.exists():
        print(f"Arquivo não encontrado: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"{len(chunks)} chunks encontrados.")

    model = load_embedding_model(model_name) if model_name else load_embedding_model()

    texts = [chunk["text"] for chunk in chunks]

    print("Gerando embeddings...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    embedded_chunks = []

    for chunk, embedding in tqdm(
        zip(chunks, embeddings),
        total=len(chunks),
        desc="Salvando"
    ):

        embedded_chunks.append(
            {
                "id": chunk["id"],
                "text": chunk["text"],
                "embedding": embedding.tolist(),
                "metadata": chunk["metadata"],
                "content_hash": chunk["content_hash"],
            }
        )

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            embedded_chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("Embeddings gerados com sucesso!")
    print(f"Arquivo salvo em: {output_file}")


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        type=str,
        default=None,
    )

    parser.add_argument(
        "--input-file",
        type=Path,
        default=INPUT_FILE,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
    )

    parser.add_argument(
        "--output-file",
        type=Path,
        default=OUTPUT_FILE,
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    main(
        input_file=args.input_file,
        output_dir=args.output_dir,
        output_file=args.output_file,
        model_name=args.model,
    )