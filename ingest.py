"""
RAG ingestion pipeline for My Student Support Assistant.

Loads documents, creates embeddings, splits content into chunks,
and stores the vectors in ChromaDB.
"""

from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config import settings
from logging_config import get_logger
from rag.loader import load_documents
from rag.embeddings import get_embeddings

logger = get_logger(__name__)


def create_chunks(documents: List[dict]) -> List[Document]:
    """Split loaded documents into smaller searchable chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )

    chunks = []

    for item in documents:

        text = item.get("text", "").strip()

        if not text:
            continue

        metadata = {
            "source": item.get("source", "unknown"),
            "page": item.get("page", 1),
        }

        split_texts = splitter.split_text(text)

        for chunk in split_texts:

            chunks.append(
                Document(
                    page_content=chunk,
                    metadata=metadata,
                )
            )

    logger.info(
        f"Created {len(chunks)} document chunks."
    )

    return chunks


def get_vector_store():
    """Create or load the persistent Chroma vector store."""

    from langchain_chroma import Chroma

    persist_directory = Path(
        settings.CHROMA_PERSIST_DIR
    )

    persist_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(persist_directory),
    )


def ingest_documents(force: bool = False):
    """
    Load documents and add their chunks to ChromaDB.

    If force=False, ingestion is skipped when the collection
    already contains documents.
    """

    vector_store = get_vector_store()

    try:
        collection = vector_store._collection
        existing_count = collection.count()
    except Exception:
        existing_count = 0

    if existing_count > 0 and not force:
        logger.info(
            f"ChromaDB already contains {existing_count} chunks. "
            "Skipping ingestion."
        )
        return vector_store

    documents = load_documents()

    if not documents:
        logger.warning(
            "No documents found for RAG ingestion."
        )
        return vector_store

    chunks = create_chunks(documents)

    if not chunks:
        logger.warning(
            "No valid chunks were created."
        )
        return vector_store

    if force and existing_count > 0:
        try:
            collection.delete(
                where={}
            )
            logger.info(
                "Existing ChromaDB collection cleared."
            )
        except Exception as e:
            logger.warning(
                f"Could not clear existing collection: {e}"
            )

    vector_store.add_documents(chunks)

    logger.info(
        f"Successfully ingested {len(chunks)} chunks into ChromaDB."
    )

    return vector_store