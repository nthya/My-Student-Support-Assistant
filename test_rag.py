"""
Tests for the RAG pipeline: loading, chunking, ingestion, retrieval.
Run with: pytest tests/test_rag.py -v
"""
from rag.loader import load_all_documents
from rag.ingest import ingest_documents
from rag.retriever import retrieve


def test_load_documents():
    segments = load_all_documents()
    assert len(segments) > 0, "Expected demo documents to be loaded"
    assert all(seg.source and seg.text for seg in segments)


def test_ingest_documents():
    count = ingest_documents(force=True)
    assert count > 0, "Expected chunks to be stored in ChromaDB"


def test_retrieve_attendance_question():
    ingest_documents(force=False)
    results = retrieve("What is the attendance requirement?", k=3)
    assert len(results) > 0
    combined_text = " ".join(r.text.lower() for r in results)
    assert "attendance" in combined_text
    assert all(r.source for r in results)
