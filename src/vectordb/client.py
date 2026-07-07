from pathlib import Path
from typing import TYPE_CHECKING

import chromadb

if TYPE_CHECKING:
    from chromadb.api import ClientAPI
    from chromadb.api.models.Collection import Collection

DEFAULT_PERSIST_DIR = Path("data/vectordb/chroma")
DEFAULT_COLLECTION_NAME = "clinical_docs"


def get_client(persist_dir: Path | None = None) -> "ClientAPI":
    """Cria (ou reabre) o client persistente do Chroma."""

    persist_dir = persist_dir or DEFAULT_PERSIST_DIR
    persist_dir.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(path=str(persist_dir))


def get_or_create_collection(
    client: "ClientAPI",
    name: str = DEFAULT_COLLECTION_NAME,
) -> "Collection":
    """Obtém a collection, criando-a com métrica de cosseno se necessário."""

    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
