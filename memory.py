"""
Conversational memory.

Two layers are used:
1. LangGraph's SqliteSaver checkpointer - gives the agent automatic
   short-term memory of the running conversation (thread-scoped).
2. A custom long-term layer backed by the `students` and `chat_messages`
   SQLite tables - stores durable facts (name, department, year, semester)
   and the full chat transcript so history survives server restarts and
   can be shown in the UI / fetched via the API.
"""
import json
import re
import sqlite3
from typing import Optional

from langgraph.checkpoint.sqlite import SqliteSaver

from config import settings
from database.database import get_db_context
from database.models import Student, ChatSession, ChatMessage, Department
from logging_config import get_logger

logger = get_logger(__name__)

_CHECKPOINT_DB_PATH = "./data/checkpoints.sqlite"

# --- Simple pattern-based profile extraction -------------------------------
# NOTE: this is a lightweight heuristic extractor (regex based) intended for
# a demo/college-assistant use case. For production use, consider a small
# structured-extraction call to the LLM instead.

_DEPT_PATTERN = re.compile(r"\b(CSE|ECE|MECH|CIVIL|IT|EEE)\b", re.IGNORECASE)
_YEAR_PATTERN = re.compile(
    r"\b(1st|2nd|3rd|4th|first|second|third|fourth)\s+year\b", re.IGNORECASE
)
_NAME_PATTERN = re.compile(r"\bmy name is\s+([A-Za-z]+)", re.IGNORECASE)

_YEAR_WORDS = {
    "1st": 1, "first": 1,
    "2nd": 2, "second": 2,
    "3rd": 3, "third": 3,
    "4th": 4, "fourth": 4,
}


def _get_checkpointer_conn():
    """SqliteSaver requires its own sqlite connection (separate from SQLAlchemy)."""
    conn = sqlite3.connect(_CHECKPOINT_DB_PATH, check_same_thread=False)
    return conn


def get_checkpointer() -> SqliteSaver:
    """Returns the LangGraph checkpointer used for short-term thread memory."""
    conn = _get_checkpointer_conn()
    return SqliteSaver(conn)


def extract_profile_facts(text: str) -> dict:
    """Extract department/year/name mentions from a user message, if present."""
    facts = {}

    dept_match = _DEPT_PATTERN.search(text)
    if dept_match:
        facts["department_code"] = dept_match.group(1).upper()

    year_match = _YEAR_PATTERN.search(text)
    if year_match:
        word = year_match.group(1).lower()
        facts["year"] = _YEAR_WORDS.get(word)

    name_match = _NAME_PATTERN.search(text)
    if name_match:
        facts["name"] = name_match.group(1).capitalize()

    return facts


def update_student_profile(student_id: int, facts: dict) -> None:
    """Persist extracted profile facts to the students table."""
    if not facts:
        return
    with get_db_context() as db:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return
        if "name" in facts:
            student.name = facts["name"]
        if "department_code" in facts:
            dept = db.query(Department).filter(Department.code == facts["department_code"]).first()
            if dept:
                student.department_id = dept.id
        if "year" in facts:
            student.year = facts["year"]
        db.commit()
        logger.info(f"Updated profile for student {student_id}: {facts}")


def get_student_context(student_id: Optional[int]) -> str:
    """Build a short natural-language context string describing the student."""
    if not student_id:
        return ""
    with get_db_context() as db:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return ""
        parts = []
        if student.name:
            parts.append(f"Name: {student.name}")
        if student.department:
            parts.append(f"Department: {student.department.code}")
        if student.year:
            parts.append(f"Year: {student.year}")
        if student.semester:
            parts.append(f"Semester: {student.semester}")
        return "; ".join(parts)


def save_message(session_id: str, role: str, content: str, sources: list = None) -> None:
    """Persist a chat message to SQLite (long-term durable history)."""
    with get_db_context() as db:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(id=session_id, title=content[:50])
            db.add(session)
            db.commit()
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=json.dumps(sources) if sources else None,
        )
        db.add(msg)
        db.commit()


def get_history(session_id: str) -> list:
    """Return the full persisted chat transcript for a session."""
    with get_db_context() as db:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .all()
        )
        return [
            {
                "role": m.role,
                "content": m.content,
                "sources": json.loads(m.sources) if m.sources else [],
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]
