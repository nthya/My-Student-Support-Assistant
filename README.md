# My Student Support Assistant

A personalized AI-based student support assistant built using
FastAPI, RAG, LangGraph, tools, memory, and a locally hosted
language model.

## Overview

My Student Support Assistant is designed to help students with
academic information, study-related questions, college resources,
and general student support.

The application uses Retrieval-Augmented Generation (RAG) to
retrieve relevant information from the available knowledge
documents before generating an answer.

The system is designed as a local-first application, so the main
AI processing can run locally using Ollama.

---

## Main Features

- AI-powered student support chat
- Retrieval-Augmented Generation (RAG)
- Local LLM using Ollama
- Qwen 2.5 model support
- ChromaDB vector database
- Sentence Transformer embeddings
- LangGraph-based agent workflow
- Tool-based student information retrieval
- Conversation memory
- SQLite database
- FastAPI backend
- HTML, CSS and JavaScript frontend
- Sample academic and examination information
- Automated tests

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy

### AI / LLM

- Qwen 2.5
- Ollama
- LangChain
- LangGraph

### RAG

- ChromaDB
- Sentence Transformers
- Recursive Character Text Splitter

### Database

- SQLite
- SQLAlchemy

### Frontend

- HTML
- CSS
- JavaScript

### Testing

- Pytest

---

## Project Structure

```text
My-Student-Support-Assistant/
│
├── agent/
│   ├── prompts.py
│   └── tools.py
│
├── api/
│   ├── routes.py
│   └── schemas.py
│
├── data/
│   └── documents/
│
├── database/
│   ├── database.py
│   ├── models.py
│   └── seed.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── llm/
│   └── gemma.py
│
├── memory/
│   └── memory.py
│
├── rag/
│   ├── embeddings.py
│   ├── ingest.py
│   ├── loader.py
│   └── retriever.py
│
├── tests/
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_memory.py
│   ├── test_rag.py
│   └── test_tools.py
│
├── app.py
├── config.py
├── logging_config.py
├── requirements.txt
├── .env.example
└── README.md