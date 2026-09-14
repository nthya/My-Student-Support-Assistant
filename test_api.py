"""
Tests for FastAPI endpoints (excluding /chat, which requires a running Ollama server).
Run with: pytest tests/test_api.py -v
"""
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_create_and_get_student():
    res = client.post("/api/students", json={"name": "Test User", "department_code": "CSE", "year": 3})
    assert res.status_code == 200
    student_id = res.json()["id"]

    res2 = client.get(f"/api/students/{student_id}")
    assert res2.status_code == 200
    assert res2.json()["name"] == "Test User"


def test_list_notices():
    res = client.get("/api/notices")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_list_exam_schedule():
    res = client.get("/api/exam-schedule?department_code=CSE")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_list_subjects():
    res = client.get("/api/subjects?department_code=CSE&year=3")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
