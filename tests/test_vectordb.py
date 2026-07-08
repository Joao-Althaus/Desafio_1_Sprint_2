import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import chromadb
import numpy as np

from src.vectordb import client as vectordb_client
from src.vectordb import query as vectordb_query
from src.vectordb import store


def fake_chunks() -> list[dict]:
    return [
        {
            "id": "doc_1_chunk_0",
            "text": "Texto clínico de teste.",
            "content_hash": "abc123",
            "embedding": [0.1, 0.2, 0.3],
            "metadata": {
                "document_id": "doc_1",
                "chunk_number": 0,
                "page_start": 1,
                "page_end": 1,
            },
        },
        {
            "id": "doc_1_chunk_1",
            "text": "Outro trecho de teste.",
            "content_hash": "def456",
            "embedding": [0.4, 0.5, 0.6],
            "metadata": {
                "document_id": "doc_1",
                "chunk_number": 1,
                "page_start": 1,
                "page_end": 2,
            },
        },
    ]


class ClientTests(unittest.TestCase):

    def test_get_or_create_collection_uses_cosine_metric(self):

        client = chromadb.EphemeralClient()
        collection = vectordb_client.get_or_create_collection(
            client, "test_collection"
        )

        self.assertEqual(collection.metadata["hnsw:space"], "cosine")


class StoreTests(unittest.TestCase):

    def test_main_stores_all_chunks(self):

        with tempfile.TemporaryDirectory() as tmp_dir:

            input_file = Path(tmp_dir) / "embeddings.json"
            input_file.write_text(
                json.dumps(fake_chunks()), encoding="utf-8"
            )

            collection = store.main(
                embeddings_file=input_file,
                collection_name="test_store",
                client=chromadb.EphemeralClient(),
            )

            self.assertEqual(collection.count(), 2)

    def test_main_upsert_is_idempotent(self):

        with tempfile.TemporaryDirectory() as tmp_dir:

            input_file = Path(tmp_dir) / "embeddings.json"
            input_file.write_text(
                json.dumps(fake_chunks()), encoding="utf-8"
            )

            fake_client = chromadb.EphemeralClient()

            store.main(
                embeddings_file=input_file,
                collection_name="test_idem",
                client=fake_client,
            )
            collection = store.main(
                embeddings_file=input_file,
                collection_name="test_idem",
                client=fake_client,
            )

            self.assertEqual(collection.count(), 2)

    def test_metadata_includes_content_hash(self):

        with tempfile.TemporaryDirectory() as tmp_dir:

            input_file = Path(tmp_dir) / "embeddings.json"
            input_file.write_text(
                json.dumps(fake_chunks()), encoding="utf-8"
            )

            collection = store.main(
                embeddings_file=input_file,
                collection_name="test_meta",
                client=chromadb.EphemeralClient(),
            )

            record = collection.get(
                ids=["doc_1_chunk_0"], include=["metadatas"]
            )

            self.assertEqual(
                record["metadatas"][0]["content_hash"], "abc123"
            )


class FakeModel:
    """Simula o SentenceTransformer sempre apontando pra perto de docA/chunk 0."""

    def encode(self, texts, **kwargs):
        return [np.array([1.0, 0.0, 0.0]) for _ in texts]


class QueryTests(unittest.TestCase):

    def _collection_with_fixtures(self, name: str):

        client = chromadb.EphemeralClient()
        collection = vectordb_client.get_or_create_collection(client, name)

        collection.upsert(
            ids=["a0", "a1", "a2", "b0"],
            embeddings=[
                [1.0, 0.0, 0.0],
                [0.9, 0.1, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
            ],
            documents=[
                "informação sobre losartana dose",
                "mais detalhes sobre losartana",
                "outro assunto do documento A",
                "conteúdo do documento B",
            ],
            metadatas=[
                {"document_id": "docA", "chunk_number": 0},
                {"document_id": "docA", "chunk_number": 1},
                {"document_id": "docA", "chunk_number": 2},
                {"document_id": "docB", "chunk_number": 0},
            ],
        )

        return collection

    def test_search_returns_closest_match(self):

        collection = self._collection_with_fixtures("test_search")

        with patch.object(
            vectordb_query, "_get_model", return_value=FakeModel()
        ):
            results = vectordb_query.search(collection, "qualquer pergunta", top_k=1)

        self.assertEqual(results[0]["id"], "a0")

    def test_search_filters_by_document_id(self):

        collection = self._collection_with_fixtures("test_search_doc")

        with patch.object(
            vectordb_query, "_get_model", return_value=FakeModel()
        ):
            results = vectordb_query.search(
                collection, "qualquer pergunta", top_k=10, document_id="docB"
            )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "b0")

    def test_search_filters_by_contains(self):

        collection = self._collection_with_fixtures("test_search_contains")

        with patch.object(
            vectordb_query, "_get_model", return_value=FakeModel()
        ):
            results = vectordb_query.search(
                collection, "qualquer pergunta", top_k=10, contains="losartana"
            )

        result_ids = {result["id"] for result in results}
        self.assertEqual(result_ids, {"a0", "a1"})

    def test_get_neighbors_returns_window_sorted_by_chunk_number(self):

        collection = self._collection_with_fixtures("test_neighbors")

        neighbors = vectordb_query.get_neighbors(
            collection, document_id="docA", chunk_number=1, window=1
        )

        self.assertEqual(
            [chunk["id"] for chunk in neighbors], ["a0", "a1", "a2"]
        )

    def test_list_document_ids_returns_distinct_sorted_ids(self):

        collection = self._collection_with_fixtures("test_list_docs")

        self.assertEqual(
            vectordb_query.list_document_ids(collection), ["docA", "docB"]
        )


if __name__ == "__main__":
    unittest.main()
