import argparse
import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.vectordb.client import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_PERSIST_DIR,
    get_client,
    get_or_create_collection,
)

if TYPE_CHECKING:
    from chromadb.api import ClientAPI
    from chromadb.api.models.Collection import Collection

EMBEDDING_FILE = Path("data/embeddings/embeddings.json")
BATCH_SIZE = 200


def main(
    embeddings_file: Path | None = None,
    persist_dir: Path | None = None,
    collection_name: str | None = None,
    client: "ClientAPI | None" = None,
) -> "Collection | None":
    """Lê data/embeddings/embeddings.json e faz upsert em batch no Chroma."""

    embeddings_file = embeddings_file or EMBEDDING_FILE
    persist_dir = persist_dir or DEFAULT_PERSIST_DIR
    collection_name = collection_name or DEFAULT_COLLECTION_NAME

    if not embeddings_file.exists():
        print(f"Arquivo não encontrado: {embeddings_file}")
        return None

    with open(embeddings_file, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print(f"{len(chunks)} chunks encontrados.")

    client = client or get_client(persist_dir)
    collection = get_or_create_collection(client, collection_name)

    print("Enviando embeddings para o Chroma...")

    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]

        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            documents=[chunk["text"] for chunk in batch],
            metadatas=[
                {**chunk["metadata"], "content_hash": chunk["content_hash"]}
                for chunk in batch
            ],
        )

    print()
    print("Embeddings armazenados com sucesso!")
    print(f"Total na collection '{collection_name}': {collection.count()}")

    return collection


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Armazena os embeddings gerados em uma collection do Chroma"
    )

    parser.add_argument("--input-file", type=Path, default=EMBEDDING_FILE)
    parser.add_argument("--persist-dir", type=Path, default=DEFAULT_PERSIST_DIR)
    parser.add_argument(
        "--collection-name", type=str, default=DEFAULT_COLLECTION_NAME
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    main(
        embeddings_file=args.input_file,
        persist_dir=args.persist_dir,
        collection_name=args.collection_name,
    )
