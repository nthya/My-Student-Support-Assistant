"""
Document loader for My Student Support Assistant.

Loads text and PDF documents from the configured documents directory.
"""

from pathlib import Path
from typing import List, Dict

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)


def load_text_file(path: Path) -> List[Dict]:
    """Load a text file and return its content with source information."""

    try:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()

        if not text.strip():
            return []

        return [
            {
                "text": text,
                "source": path.name,
                "page": 1,
            }
        ]

    except Exception as e:
        logger.error(
            f"Failed to load text file {path}: {e}"
        )
        return []


def load_pdf_file(path: Path) -> List[Dict]:
    """Load text from a PDF document."""

    documents = []

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))

        for page_number, page in enumerate(reader.pages, start=1):

            text = page.extract_text() or ""

            if text.strip():
                documents.append(
                    {
                        "text": text,
                        "source": path.name,
                        "page": page_number,
                    }
                )

    except Exception as e:
        logger.error(
            f"Failed to load PDF file {path}: {e}"
        )

    return documents


def load_documents() -> List[Dict]:
    """
    Load all supported documents from the configured
    documents directory.
    """

    documents_dir = Path(settings.DOCUMENTS_DIR)

    if not documents_dir.exists():
        logger.warning(
            f"Documents directory not found: {documents_dir}"
        )
        return []

    documents = []

    # -------------------------------------------------
    # Load TXT files
    # -------------------------------------------------

    for path in documents_dir.glob("*.txt"):

        logger.info(
            f"Loading text document: {path.name}"
        )

        documents.extend(
            load_text_file(path)
        )

    # -------------------------------------------------
    # Load PDF files
    # -------------------------------------------------

    for path in documents_dir.glob("*.pdf"):

        logger.info(
            f"Loading PDF document: {path.name}"
        )

        documents.extend(
            load_pdf_file(path)
        )

    logger.info(
        f"Loaded {len(documents)} document pages/chunks."
    )

    return documents