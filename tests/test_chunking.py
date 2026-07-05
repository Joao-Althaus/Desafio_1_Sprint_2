import json
import tempfile
import unittest
from pathlib import Path
from src.chunking import chunking


class ChunkingTests(unittest.TestCase):
    def test_main_generates_chunks_from_processed_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            processed_dir = tmp_path / "processed"
            chunked_dir = tmp_path / "chunked"
            processed_dir.mkdir()
            chunked_dir.mkdir()
            output_file = chunked_dir / "chunks.json"

            # Make sure the processed directory is empty to simulate the test case
            # The document created here does not simulate the actual structure of the processed `documentos.json`; it is used solely for illustrative purposes.
            fake_documents = [
                {
                    "document_id": "bula_teste",
                    "page": 1,
                    "text": "Texto da página inicial. Contém indicações do remédio."
                },
                {
                    "document_id": "bula_teste",
                    "page": 2,
                    "text": "Texto da segunda página. Contém efeitos colaterais."
                }
            ]

            processed_data_file = processed_dir / "documents.json"
            processed_data_file.write_text(json.dumps(fake_documents), encoding="utf-8")

            chunking.main(
                processed_dir=processed_dir, 
                chunked_dir=chunked_dir, 
                output_file=output_file
            )

            # Read the generated chunks.json file and validate its contents
            self.assertTrue(output_file.exists(), "O arquivo chunks.json não foi gerado.")
            saved_chunks = json.loads(output_file.read_text(encoding="utf-8"))

            # Validate the structure and content of the generated chunks
            self.assertGreaterEqual(len(saved_chunks), 1, "Nenhum chunk foi gerado.")
            
            first_chunk = saved_chunks[0]

            # verification of the chunk structure
            self.assertTrue(first_chunk["id"].startswith("bula_teste_chunk_"))
            self.assertIn("content_hash", first_chunk)
            
            # Verification of the text content and page tags
            self.assertIn("Texto da página inicial", first_chunk["text"])
            self.assertIn("Texto da segunda página", first_chunk["text"])
            self.assertNotIn("[PAGE 1]", first_chunk["text"], "A tag da página não foi removida.")
            
            # Verificayion of the metadata
            metadata = first_chunk["metadata"]
            self.assertEqual(metadata["document_id"], "bula_teste")
            self.assertEqual(metadata["page_start"], 1)
            self.assertEqual(metadata["page_end"], 2)

    def test_main_exits_gracefully_when_no_data_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            processed_dir = tmp_path / "processed"
            chunked_dir = tmp_path / "chunked"
            processed_dir.mkdir()


            try:
                chunking.main(processed_dir=processed_dir, chunked_dir=chunked_dir)
                success = True
            except Exception:
                success = False

            self.assertTrue(success, "O código quebrou ao lidar com uma pasta sem documentos.")


if __name__ == "__main__":
    unittest.main()