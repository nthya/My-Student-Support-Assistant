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
Requirements

Before running the application, install:

Python 3.11 or later
Ollama
Qwen 2.5 model
Installation
1. Clone the repository
git clone https://github.com/nthya/My-Student-Support-Assistant.git
cd My-Student-Support-Assistant
2. Create a virtual environment
python -m venv venv
3. Activate the environment

Windows:

venv\Scripts\activate

Linux / macOS:

source venv/bin/activate
4. Install dependencies
pip install -r requirements.txt
Ollama Setup

Install Ollama and download the Qwen 2.5 model:

ollama pull qwen2.5:3b

Make sure Ollama is running before starting the application.

Environment Configuration

Create a local .env file using .env.example:

OLLAMA_BASE_URL=http://localhost:11434
GEMMA_MODEL=qwen2.5:3b

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

DATABASE_URL=sqlite:///./data/student_support.db

CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=college_docs

DOCUMENTS_DIR=./data/documents
CHUNK_SIZE=500
CHUNK_OVERLAP=50
RAG_TOP_K=4

APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

Do not upload the .env file to GitHub.

Running the Application

Run:

python app.py

Or:

uvicorn app:app --reload --port 8000

Open the application in a browser:

http://localhost:8000
RAG Knowledge Documents

The application can use documents stored inside:

data/documents/

Supported document types include:

.txt
.pdf

These documents are processed into smaller chunks and stored
in ChromaDB for semantic retrieval.

Sample Data

The project contains sample academic data for demonstration
and educational purposes.

The sample information is fictional/demo data and should not be
treated as official information from any college or university.

Testing

Run the test suite using:

pytest
Disclaimer

My Student Support Assistant is an educational project.

The generated answers may contain mistakes or incomplete
information. Users should verify important academic information
with official college or university sources.

Source Acknowledgement

This internship version is based on the open-source
AI Student Support Assistant project by MO1510-SHREE.

The original project served as the architectural and
implementation starting point. This repository is maintained as
a customized educational version for learning, experimentation,
and internship demonstration.

Original project:

https://github.com/MO1510-SHREE/AI-Student-Support-Assistant

Project Purpose

This project was developed as part of an educational and
internship learning experience to understand:

AI application development
RAG pipelines
Local LLM integration
FastAPI development
Vector databases
Agent workflows
Database integration
Frontend and backend integration
Software testing
License

This project is intended for educational and demonstration
purposes.
