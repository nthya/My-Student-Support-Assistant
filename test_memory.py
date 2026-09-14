"""
Tests for the memory / profile-extraction module.
Run with: pytest tests/test_memory.py -v
"""
from database.database import init_db, SessionLocal
from database.seed import run_seed
from database.models import Student
from memory.memory import extract_profile_facts, update_student_profile, get_student_context


def setup_module(module):
    init_db()
    run_seed()


def test_extract_profile_facts_department_and_year():
    facts = extract_profile_facts("I am a CSE student in 3rd year.")
    assert facts.get("department_code") == "CSE"
    assert facts.get("year") == 3


def test_extract_profile_facts_name():
    facts = extract_profile_facts("Hi, my name is Arun.")
    assert facts.get("name") == "Arun"


def test_update_and_get_student_context():
    db = SessionLocal()
    student = Student()
    db.add(student)
    db.commit()
    db.refresh(student)
    student_id = student.id
    db.close()

    update_student_profile(student_id, {"department_code": "CSE", "year": 3})
    context = get_student_context(student_id)
    assert "CSE" in context
    assert "3" in context
