import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.ingestion import ingest


class FakePage:
    def __init__(self, content: str, page_number: int = 1):
        self.page_content = content
        self.metadata = {"page": page_number - 1}


class FakePyPDFLoader:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def load(self):
        return [FakePage("  Exemplo de texto clínico  ", page_number=1)]


class IngestTests(unittest.TestCase):
    def test_main_writes_processed_documents_for_temp_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            raw_dir = tmp_path / "raw"
            processed_dir = tmp_path / "processed"
            raw_dir.mkdir()
            processed_dir.mkdir()
            output_file = processed_dir / "documents.json"
            (raw_dir / "sample.pdf").write_bytes(b"fake-pdf")

            with patch("src.ingestion.ingest.PyPDFLoader", FakePyPDFLoader):
                ingest.main(raw_dir=raw_dir, processed_dir=processed_dir, output_file=output_file)

            saved_documents = json.loads(output_file.read_text(encoding="utf-8"))

            self.assertEqual(len(saved_documents), 1)
            self.assertEqual(saved_documents[0]["document_name"], "sample")
            self.assertEqual(saved_documents[0]["text"], "Exemplo de texto clínico")


if __name__ == "__main__":
    unittest.main()
