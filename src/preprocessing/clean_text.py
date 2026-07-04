import re


def clean_text(text: str | None) -> str:
    """Normalize raw text extracted from PDFs for downstream ingestion."""
    if not text:
        return ""

    cleaned_text = text.replace("\xa0", " ")
    cleaned_text = re.sub(r"[\t\r\f\v]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)
    return cleaned_text.strip()
