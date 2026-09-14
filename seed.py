"""
Seed sample data for My Student Support Assistant.

The data below is demo/educational data and is not official
college information.
"""

from database.database import SessionLocal
from database.models import Department, Subject, Notice, Exam, AcademicCalendar
from logging_config import get_logger

logger = get_logger(__name__)


def run_seed():
    """Insert sample AI & ML academic data if the database is empty."""

    db = SessionLocal()

    try:
        # -------------------------------------------------
        # Departments
        # -------------------------------------------------

        departments = [
            ("AIML", "Artificial Intelligence and Machine Learning"),
            ("CSE", "Computer Science and Engineering"),
            ("ECE", "Electronics and Communication Engineering"),
            ("MECH", "Mechanical Engineering"),
        ]

        for code, name in departments:
            existing = (
                db.query(Department)
                .filter(Department.code == code)
                .first()
            )

            if not existing:
                db.add(
                    Department(
                        code=code,
                        name=name,
                    )
                )

        db.commit()

        # -------------------------------------------------
        # Subjects
        # -------------------------------------------------

        aiml_department = (
            db.query(Department)
            .filter(Department.code == "AIML")
            .first()
        )

        if aiml_department:

            subjects = [
                ("Machine Learning", "AIML"),
                ("Deep Learning", "AIML"),
                ("Natural Language Processing", "AIML"),
                ("Data Analytics", "AIML"),
                ("Python Programming", "AIML"),
                ("Artificial Intelligence", "AIML"),
            ]

            for subject_name, dept_code in subjects:

                existing = (
                    db.query(Subject)
                    .filter(
                        Subject.name == subject_name,
                        Subject.department_id == aiml_department.id,
                    )
                    .first()
                )

                if not existing:
                    db.add(
                        Subject(
                            name=subject_name,
                            department_id=aiml_department.id,
                        )
                    )

        db.commit()

        # -------------------------------------------------
        # Sample Notices
        # -------------------------------------------------

        notices = [
            (
                "Internal Assessment",
                "Students are advised to prepare for the upcoming internal assessment.",
            ),
            (
                "Project Review",
                "Final year students should keep their project documentation ready for review.",
            ),
            (
                "Placement Preparation",
                "Students can practice aptitude, SQL, Python, Excel and communication skills for placement preparation.",
            ),
        ]

        for title, description in notices:

            existing = (
                db.query(Notice)
                .filter(Notice.title == title)
                .first()
            )

            if not existing:
                db.add(
                    Notice(
                        title=title,
                        description=description,
                    )
                )

        db.commit()

        # -------------------------------------------------
        # Sample Exams
        # -------------------------------------------------

        exams = [
            ("Internal Assessment 1", "AIML"),
            ("Internal Assessment 2", "AIML"),
            ("Model Examination", "AIML"),
            ("Semester Examination", "AIML"),
        ]

        for exam_name, dept_code in exams:

            existing = (
                db.query(Exam)
                .filter(Exam.name == exam_name)
                .first()
            )

            if not existing:
                db.add(
                    Exam(
                        name=exam_name,
                        department=dept_code,
                    )
                )

        db.commit()

        # -------------------------------------------------
        # Academic Calendar
        # -------------------------------------------------

        calendar_items = [
            (
                "Semester Start",
                "Beginning of the academic semester",
            ),
            (
                "Internal Assessment",
                "Internal assessment period",
            ),
            (
                "Project Review",
                "Project review and evaluation",
            ),
            (
                "Semester Examination",
                "End semester examination period",
            ),
        ]

        for title, description in calendar_items:

            existing = (
                db.query(AcademicCalendar)
                .filter(AcademicCalendar.title == title)
                .first()
            )

            if not existing:
                db.add(
                    AcademicCalendar(
                        title=title,
                        description=description,
                    )
                )

        db.commit()

        logger.info(
            "Sample academic seed data loaded successfully."
        )

    except Exception as e:

        db.rollback()

        logger.error(
            f"Failed to seed sample data: {e}"
        )

    finally:

        db.close()