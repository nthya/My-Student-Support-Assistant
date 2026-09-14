import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)

from sqlalchemy.orm import Session

from config import settings

from database.database import get_db

from database.models import (
    Student,
    Department,
    Notice,
    ExamSchedule,
    Subject,
)

from api.schemas import (
    ChatRequest,
    ChatResponse,
    SourceItem,
    StudentCreate,
    StudentResponse,
    ChatMessageResponse,
    NoticeResponse,
    ExamScheduleResponse,
    SubjectResponse,
)

from agent.graph import build_graph

from memory.memory import (
    get_checkpointer,
    save_message,
    get_history,
)

from rag.ingest import ingest_documents

from logging_config import get_logger


# =========================================================
# LOGGER
# =========================================================

logger = get_logger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# AI AGENT
# =========================================================

_checkpointer = get_checkpointer()

_agent = build_graph(
    checkpointer=_checkpointer
)


# =========================================================
# DOCUMENTS
# =========================================================


@router.get("/documents")
def list_documents():
    """
    Return all documents currently stored in the
    RAG knowledge-base folder.
    """

    docs_dir = settings.DOCUMENTS_DIR

    # If folder doesn't exist
    if not os.path.isdir(docs_dir):

        return []

    documents = []

    for filename in sorted(os.listdir(docs_dir)):

        full_path = os.path.join(
            docs_dir,
            filename
        )

        # Only files
        if not os.path.isfile(full_path):
            continue

        # Only PDF/TXT
        extension = os.path.splitext(
            filename
        )[1].lower()

        if extension not in {".pdf", ".txt"}:
            continue

        file_size = os.path.getsize(
            full_path
        )

        documents.append(
            {
                "filename": filename,
                "name": filename,
                "size": file_size,
                "size_kb": round(
                    file_size / 1024,
                    1
                ),
            }
        )

    return documents


# =========================================================
# UPLOAD DOCUMENT
# =========================================================


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Upload a PDF/TXT document into the RAG knowledge base.

    Process:

    1. Receive uploaded file
    2. Validate extension
    3. Save file
    4. Re-ingest documents
    5. Update ChromaDB
    6. Return result
    """

    # -----------------------------------------------------
    # Check filename
    # -----------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )


    # -----------------------------------------------------
    # Secure filename
    # -----------------------------------------------------

    safe_filename = os.path.basename(
        file.filename
    )


    # -----------------------------------------------------
    # Get extension
    # -----------------------------------------------------

    extension = os.path.splitext(
        safe_filename
    )[1].lower()


    # -----------------------------------------------------
    # Validate extension
    # -----------------------------------------------------

    allowed_extensions = {
        ".txt",
        ".pdf",
    }

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported"
        )


    # -----------------------------------------------------
    # Documents directory
    # -----------------------------------------------------

    docs_dir = settings.DOCUMENTS_DIR

    os.makedirs(
        docs_dir,
        exist_ok=True
    )


    # -----------------------------------------------------
    # Destination
    # -----------------------------------------------------

    destination = os.path.join(
        docs_dir,
        safe_filename
    )


    # -----------------------------------------------------
    # Save file
    # -----------------------------------------------------

    try:

        with open(
            destination,
            "wb"
        ) as output_file:

            shutil.copyfileobj(
                file.file,
                output_file
            )

    except Exception as e:

        logger.exception(
            "Failed to save uploaded document"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {e}"
        )

    finally:

        file.file.close()


    # -----------------------------------------------------
    # Re-index documents
    # -----------------------------------------------------

    try:

        chunk_count = ingest_documents(
            force=True
        )

    except Exception as e:

        logger.exception(
            "RAG re-ingestion failed after upload"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "File was saved, but RAG "
                f"re-indexing failed: {e}"
            )
        )


    # -----------------------------------------------------
    # Log
    # -----------------------------------------------------

    logger.info(
        f"Admin uploaded document "
        f"'{safe_filename}'. "
        f"Re-indexed {chunk_count} chunks."
    )


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "filename": safe_filename,
        "status": "uploaded",
        "chunks_indexed": chunk_count,
    }


# =========================================================
# DELETE DOCUMENT
# =========================================================


@router.delete(
    "/documents/{filename}"
)
def delete_document(
    filename: str
):
    """
    Delete a document from the knowledge base
    and rebuild the RAG index.
    """

    # -----------------------------------------------------
    # Secure filename
    # -----------------------------------------------------

    safe_filename = os.path.basename(
        filename
    )


    # -----------------------------------------------------
    # Location
    # -----------------------------------------------------

    docs_dir = settings.DOCUMENTS_DIR

    target_path = os.path.join(
        docs_dir,
        safe_filename
    )


    # -----------------------------------------------------
    # Check file
    # -----------------------------------------------------

    if not os.path.isfile(
        target_path
    ):

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    # -----------------------------------------------------
    # Delete + re-index
    # -----------------------------------------------------

    try:

        os.remove(
            target_path
        )

        chunk_count = ingest_documents(
            force=True
        )

    except Exception as e:

        logger.exception(
            "Failed to delete/re-index document"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Delete or re-index failed: "
                f"{e}"
            )
        )


    # -----------------------------------------------------
    # Log
    # -----------------------------------------------------

    logger.info(
        f"Admin deleted document "
        f"'{safe_filename}'. "
        f"Re-indexed {chunk_count} chunks."
    )


    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "filename": safe_filename,
        "status": "deleted",
        "chunks_indexed": chunk_count,
    }


# =========================================================
# HEALTH
# =========================================================


@router.get("/health")
def health():

    return {
        "status": "ok"
    }


# =========================================================
# CHAT
# =========================================================


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    payload: ChatRequest
):

    session_id = (
        payload.session_id
        or str(uuid.uuid4())
    )

    try:

        # Save user message
        save_message(
            session_id,
            "user",
            payload.message
        )


        # LangGraph configuration
        config = {
            "configurable": {
                "thread_id": session_id
            }
        }


        # Run AI agent
        result = _agent.invoke(
            {
                "query": payload.message,
                "session_id": session_id,
                "student_id": payload.student_id,
                "messages": [],
            },
            config=config,
        )


        # AI answer
        answer = result.get(
            "answer",
            "I'm sorry, something went wrong."
        )


        # Sources
        sources = result.get(
            "sources",
            []
        ) or []


        # Intent
        intent = result.get(
            "intent"
        )


        # Save assistant message
        save_message(
            session_id,
            "assistant",
            answer,
            sources
        )


        # Return
        return ChatResponse(
            session_id=session_id,
            answer=answer,
            sources=[
                SourceItem(**source)
                for source in sources
            ],
            intent=intent,
        )


    except Exception as e:

        logger.exception(
            "Chat processing failed"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to process chat "
                f"message: {e}"
            )
        )


# =========================================================
# CREATE STUDENT
# =========================================================


@router.post(
    "/students",
    response_model=StudentResponse
)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db)
):

    department_id = None


    if payload.department_code:

        department = (
            db.query(Department)
            .filter(
                Department.code
                == payload.department_code.upper()
            )
            .first()
        )


        if not department:

            raise HTTPException(
                status_code=400,
                detail="Unknown department_code"
            )


        department_id = department.id


    student = Student(
        name=payload.name,
        department_id=department_id,
        year=payload.year,
        semester=payload.semester,
    )


    db.add(student)

    db.commit()

    db.refresh(student)


    return StudentResponse(
        id=student.id,
        name=student.name,
        department_code=(
            student.department.code
            if student.department
            else None
        ),
        year=student.year,
        semester=student.semester,
    )


# =========================================================
# GET STUDENT
# =========================================================


@router.get(
    "/students/{student_id}",
    response_model=StudentResponse
)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = (
        db.query(Student)
        .filter(
            Student.id == student_id
        )
        .first()
    )


    if not student:

        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )


    return StudentResponse(
        id=student.id,
        name=student.name,
        department_code=(
            student.department.code
            if student.department
            else None
        ),
        year=student.year,
        semester=student.semester,
    )


# =========================================================
# CHAT HISTORY
# =========================================================


@router.get(
    "/chat/history/{session_id}",
    response_model=list[ChatMessageResponse]
)
def chat_history(
    session_id: str
):

    return get_history(
        session_id
    )


# =========================================================
# NOTICES
# =========================================================


@router.get(
    "/notices",
    response_model=list[NoticeResponse]
)
def list_notices(
    department_code: str = None,
    db: Session = Depends(get_db)
):

    query = db.query(
        Notice
    )


    if department_code:

        query = query.filter(
            Notice.department_code
            == department_code.upper()
        )


    notices = (
        query
        .order_by(
            Notice.posted_on.desc()
        )
        .all()
    )


    return [
        NoticeResponse(
            id=notice.id,
            title=notice.title,
            content=notice.content,
            department_code=notice.department_code,
            posted_on=str(
                notice.posted_on
            ),
        )
        for notice in notices
    ]


# =========================================================
# EXAM SCHEDULE
# =========================================================


@router.get(
    "/exam-schedule",
    response_model=list[ExamScheduleResponse]
)
def list_exam_schedule(
    department_code: str = None,
    db: Session = Depends(get_db)
):

    query = db.query(
        ExamSchedule
    )


    if department_code:

        query = query.filter(
            ExamSchedule.department_code
            == department_code.upper()
        )


    exams = (
        query
        .order_by(
            ExamSchedule.exam_date
        )
        .all()
    )


    return [
        ExamScheduleResponse(
            id=exam.id,
            department_code=exam.department_code,
            year=exam.year,
            semester=exam.semester,
            subject_name=exam.subject_name,
            exam_date=str(
                exam.exam_date
            ),
            exam_time=exam.exam_time,
            room=exam.room,
        )
        for exam in exams
    ]


# =========================================================
# SUBJECTS
# =========================================================


@router.get(
    "/subjects",
    response_model=list[SubjectResponse]
)
def list_subjects(
    department_code: str = None,
    year: int = None,
    db: Session = Depends(get_db)
):

    query = db.query(
        Subject
    )


    if department_code:

        department = (
            db.query(Department)
            .filter(
                Department.code
                == department_code.upper()
            )
            .first()
        )


        if not department:

            return []


        query = query.filter(
            Subject.department_id
            == department.id
        )


    if year:

        query = query.filter(
            Subject.year == year
        )


    subjects = query.all()


    return [
        SubjectResponse(
            id=subject.id,
            name=subject.name,
            code=subject.code,
            year=subject.year,
            semester=subject.semester,
        )
        for subject in subjects
    ]