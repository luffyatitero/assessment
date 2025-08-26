from datetime import datetime

import pytest
from sqlmodel import Session, select

from models import User, Department, Course, Student, AttendanceLog


def create_user(session: Session, idx: int = 1) -> User:
    user = User(
        submitted_by="tester",
        user_type="student",
        full_name=f"Test User {idx}",
        username=f"user{idx}",
        email=f"user{idx}@example.com",
        password="secret",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_department(session: Session, idx: int = 1) -> Department:
    dept = Department(
        submitted_by="tester",
        department_name=f"Department {idx}",
    )
    session.add(dept)
    session.commit()
    session.refresh(dept)
    return dept


def create_course(session: Session, dept: Department, idx: int = 1) -> Course:
    course = Course(
        submitted_by="tester",
        course_name=f"Course {idx}",
        department_id=dept.id,
        semester="Fall",
        class_id=idx,  # indexed field
        lecture_hours=3,
    )
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


def create_student(session: Session, user: User, dept: Department, idx: int = 1) -> Student:
    student = Student(
        submitted_by="tester",
        user_id=user.id,
        department_id=dept.id,
        class_id=idx,
    )
    session.add(student)
    session.commit()
    session.refresh(student)
    return student


def create_attendance(session: Session, student: Student, course: Course, present: bool = True) -> AttendanceLog:
    log = AttendanceLog(
        submitted_by="tester",
        student_id=student.id,
        course_id=course.id,
        present=present,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def test_user_crud(session: Session):
    # Create
    created = create_user(session, 1)
    assert created.id is not None

    # Read
    fetched = session.get(User, created.id)
    assert fetched is not None
    assert fetched.username == "user1"

    # Update
    fetched.full_name = "Updated Name"
    session.add(fetched)
    session.commit()
    session.refresh(fetched)
    assert fetched.full_name == "Updated Name"

    # Delete
    session.delete(fetched)
    session.commit()
    assert session.get(User, created.id) is None


def test_department_crud(session: Session):
    dept = create_department(session, 1)
    assert dept.id is not None

    fetched = session.exec(select(Department).where(Department.department_name == "Department 1")).first()
    assert fetched is not None

    fetched.department_name = "Dept X"
    session.add(fetched)
    session.commit()
    session.refresh(fetched)
    assert fetched.department_name == "Dept X"

    session.delete(fetched)
    session.commit()
    assert session.get(Department, dept.id) is None


def test_course_crud(session: Session):
    dept = create_department(session, 2)
    course = create_course(session, dept, 10)
    assert course.id is not None

    fetched = session.exec(select(Course).where(Course.course_name == "Course 10")).first()
    assert fetched is not None
    assert fetched.department_id == dept.id

    fetched.lecture_hours = 4
    session.add(fetched)
    session.commit()
    session.refresh(fetched)
    assert fetched.lecture_hours == 4

    session.delete(fetched)
    session.commit()
    assert session.get(Course, course.id) is None


def test_student_crud(session: Session):
    user = create_user(session, 3)
    dept = create_department(session, 3)
    student = create_student(session, user, dept, 301)
    assert student.id is not None

    fetched = session.exec(select(Student).where(Student.user_id == user.id)).first()
    assert fetched is not None
    assert fetched.department_id == dept.id

    fetched.class_id = 999
    session.add(fetched)
    session.commit()
    session.refresh(fetched)
    assert fetched.class_id == 999

    session.delete(fetched)
    session.commit()
    assert session.get(Student, student.id) is None



def test_attendance_log_crud(session: Session):
    user = create_user(session, 4)
    dept = create_department(session, 4)
    student = create_student(session, user, dept, 401)
    course = create_course(session, dept, 401)

    log = create_attendance(session, student, course, present=True)
    assert log.id is not None

    fetched = session.exec(select(AttendanceLog).where(AttendanceLog.student_id == student.id)).first()
    assert fetched is not None
    assert fetched.present is True

    fetched.present = False
    session.add(fetched)
    session.commit()
    session.refresh(fetched)
    assert fetched.present is False

    session.delete(fetched)
    session.commit()
    assert session.get(AttendanceLog, log.id) is None
