from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    student_id: Optional[int] = None


class SourceItem(BaseModel):
    source: str
    page: Any


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: List[SourceItem] = []
    intent: Optional[str] = None


class StudentCreate(BaseModel):
    name: Optional[str] = None
    department_code: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None


class StudentResponse(BaseModel):
    id: int
    name: Optional[str]
    department_code: Optional[str] = None
    year: Optional[int]
    semester: Optional[int]

    class Config:
        from_attributes = True


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    sources: List[Any] = []
    created_at: str


class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str
    department_code: Optional[str]
    posted_on: str

    class Config:
        from_attributes = True


class ExamScheduleResponse(BaseModel):
    id: int
    department_code: str
    year: int
    semester: int
    subject_name: str
    exam_date: str
    exam_time: Optional[str]
    room: Optional[str]

    class Config:
        from_attributes = True


class SubjectResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]
    year: int
    semester: int

    class Config:
        from_attributes = True
