"""
Tests for LangChain tools backed by SQLite.
Run with: pytest tests/test_tools.py -v
"""
from database.database import init_db
from database.seed import run_seed
from agent.tools import (
    search_notice, get_exam_schedule, get_syllabus,
    get_department_information, get_academic_calendar,
)


def setup_module(module):
    init_db()
    run_seed()


def test_get_department_information():
    result = get_department_information.invoke({"department_code": "CSE"})
    assert "Computer Science" in result


def test_get_exam_schedule():
    result = get_exam_schedule.invoke({"department_code": "CSE", "year": 3, "semester": 5})
    assert result != "NO_RESULTS"
    assert "Database Management Systems" in result


def test_get_syllabus():
    result = get_syllabus.invoke({"department_code": "CSE", "year": 3, "semester": 5})
    assert result != "NO_RESULTS"


def test_search_notice():
    result = search_notice.invoke({"keyword": "workshop"})
    assert result != "NO_RESULTS"


def test_get_academic_calendar():
    result = get_academic_calendar.invoke({"keyword": "exam"})
    assert result != "NO_RESULTS"


def test_unknown_department_returns_no_results():
    result = get_department_information.invoke({"department_code": "XXXX"})
    assert result == "NO_RESULTS"
