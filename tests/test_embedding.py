import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np

from src.embeddings import embedding


class FakeEmbeddingModel:
    """
    Simula o SentenceTransformer.
    """

    def encode(self, texts, **kwargs):
        return [
            np.array([0.1, 0.2, 0.3])
            for _ in texts
        ]


class EmbeddingTests(unittest.TestCase):

    def test_main_generates_embeddings_file(self):

        with tempfile.TemporaryDirectory() as tmp_dir:

            tmp_path = Path(tmp_dir)

            chunk_dir = tmp_path / "chunked"
            embedding_dir = tmp_path / "embeddings"

            chunk_dir.mkdir()
            embedding_dir.mkdir()

            input_file = chunk_dir / "chunks.json"
            output_file = embedding_dir / "embeddings.json"

            fake_chunks = [
                {
                    "id": "chunk_1",
                    "text": "Texto clínico de teste.",
                    "content_hash": "abc123",
                    "metadata": {
                        "document_id": "doc_1",
                        "chunk_number": 1,
                        "page_start": 1,
                        "page_end": 1,
                    },
                }
            ]

            input_file.write_text(
                json.dumps(fake_chunks),
                encoding="utf-8",
            )

            with patch(
                "src.embeddings.embedding.load_embedding_model",
                return_value=FakeEmbeddingModel(),
            ):

                embedding.main(
                    input_file=input_file,
                    output_dir=embedding_dir,
                    output_file=output_file,
                )

            self.assertTrue(output_file.exists())

            generated = json.loads(
                output_file.read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(len(generated), 1)

            self.assertEqual(
                generated[0]["id"],
                "chunk_1",
            )

            self.assertEqual(
                generated[0]["embedding"],
                [0.1, 0.2, 0.3],
            )

            self.assertEqual(
                generated[0]["metadata"]["document_id"],
                "doc_1",
            )


if __name__ == "__main__":
    unittest.main()