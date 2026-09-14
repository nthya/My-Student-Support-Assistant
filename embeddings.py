"""
Embedding model wrapper using HuggingFace Sentence Transformers (local, free, no API key).
"""
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Returns a cached HuggingFaceEmbeddings instance so the model is loaded
    into memory only once per process.
    """
    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
