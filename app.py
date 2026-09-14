"""
My Student Support Assistant - main FastAPI application.

Run with:
    uvicorn app:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
from database.database import init_db
from database.seed import run_seed
from rag.ingest import ingest_documents
from api.routes import router as api_router
from logging_config import get_logger


logger = get_logger(__name__)


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="My Student Support Assistant",
    description=(
        "A personalized student support assistant powered by "
        "RAG, tools, memory, and a local language model."
    ),
    version="1.0.0",
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(
    api_router,
    prefix="/api"
)


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def on_startup():

    logger.info(
        "Starting My Student Support Assistant..."
    )

    # Initialize database
    init_db()

    # Insert sample seed data
    run_seed()

    # Ingest existing knowledge documents
    try:

        ingest_documents(force=False)

    except Exception as e:

        logger.error(
            f"RAG ingestion failed on startup: {e}"
        )

    logger.info(
        "My Student Support Assistant startup complete."
    )


# =========================================================
# FRONTEND STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)


# =========================================================
# HOME PAGE
# =========================================================

@app.get("/")
def serve_index():

    return FileResponse(
        "frontend/index.html"
    )


# =========================================================
# RUN DIRECTLY
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )