from functools import lru_cache
from typing import TYPE_CHECKING, Any, TypedDict

from src.embeddings.embedding_model import load_embedding_model

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection


class ChunkResult(TypedDict):
    id: str
    text: str
    metadata: dict[str, Any]


class QueryResult(ChunkResult):
    distance: float


@lru_cache(maxsize=1)
def _get_model():
    """Carrega o modelo de embeddings uma única vez (o mesmo usado na geração dos embeddings)."""

    return load_embedding_model()


def search(
    collection: "Collection",
    query_text: str,
    top_k: int = 5,
    document_id: str | None = None,
    contains: str | None = None,
) -> list[QueryResult]:
    """
    Busca semântica a partir de texto puro.

    document_id: restringe a busca a um único documento-fonte (ex.: só a bula).
    contains:    exige que o termo apareça literalmente no texto do chunk.
    """

    model = _get_model()
    query_embedding = model.encode([query_text])[0].tolist()

    where = {"document_id": document_id} if document_id else None
    where_document = {"$contains": contains} if contains else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
        where_document=where_document,
    )

    return [
        QueryResult(
            id=results["ids"][0][i],
            text=results["documents"][0][i],
            metadata=results["metadatas"][0][i],
            distance=results["distances"][0][i],
        )
        for i in range(len(results["ids"][0]))
    ]


def get_neighbors(
    collection: "Collection",
    document_id: str,
    chunk_number: int,
    window: int = 1,
) -> list[ChunkResult]:
    """Retorna o chunk indicado e seus vizinhos (chunk_number ± window) no mesmo documento."""

    record = collection.get(
        where={
            "$and": [
                {"document_id": {"$eq": document_id}},
                {"chunk_number": {"$gte": chunk_number - window}},
                {"chunk_number": {"$lte": chunk_number + window}},
            ]
        },
    )

    neighbors = [
        ChunkResult(
            id=record["ids"][i],
            text=record["documents"][i],
            metadata=record["metadatas"][i],
        )
        for i in range(len(record["ids"]))
    ]

    return sorted(neighbors, key=lambda chunk: chunk["metadata"]["chunk_number"])


def list_document_ids(collection: "Collection") -> list[str]:
    """Lista os document_id distintos presentes na collection."""

    record = collection.get(include=["metadatas"])

    return sorted({metadata["document_id"] for metadata in record["metadatas"]})
