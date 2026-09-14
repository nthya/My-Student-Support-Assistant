"""
Tests for database models and seeding.
Run with: pytest tests/test_database.py -v
"""
from database.database import init_db, SessionLocal
from database.seed import run_seed
from database.models import Department, Subject, Notice, ExamSchedule, AcademicCalendar


def setup_module(module):
    init_db()
    run_seed()


def test_departments_seeded():
    db = SessionLocal()
    count = db.query(Department).count()
    db.close()
    assert count >= 4


def test_subjects_seeded():
    db = SessionLocal()
    count = db.query(Subject).count()
    db.close()
    assert count > 0


def test_notices_seeded():
    db = SessionLocal()
    count = db.query(Notice).count()
    db.close()
    assert count > 0


def test_exam_schedule_seeded():
    db = SessionLocal()
    count = db.query(ExamSchedule).count()
    db.close()
    assert count > 0


def test_academic_calendar_seeded():
    db = SessionLocal()
    count = db.query(AcademicCalendar).count()
    db.close()
    assert count > 0
