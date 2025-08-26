from typing import List, Annotated
from fastapi import APIRouter, Response, status, Depends, Body
from fastapi.responses import JSONResponse

from sqlmodel import Session

from models import (
    Student, StudentRead, Department, DepartmentRead, User, UserRead,
    Course, CourseRead, AttendanceLog, AttendanceLogRead, CourseAdd,
    AttendanceLogCreate, UserCreate, StudentCreate
    )
from db import get_session


router = APIRouter()

@router.get("/")
async def read_root():
    return JSONResponse(content={"message": "Hello, World!"}, status_code=200)

@router.get("/students", response_model=List[StudentRead])
async def read_students(session: Session = Depends(get_session)):
    students = session.query(Student).all()
    return students


@router.get("/departments", response_model=List[DepartmentRead])
async def read_departments(session: Session = Depends(get_session)):
    departments = session.query(Department).all()
    return departments

@router.get("/users", response_model=List[UserRead])
async def read_users(session: Session = Depends(get_session)):
    users = session.query(User).all()
    return users


@router.get("/courses", response_model=List[CourseRead])
async def read_courses(session: Session = Depends(get_session)):
    courses = session.query(Course).all()
    return courses

@router.post("/departments", response_model=DepartmentRead)
def add_department(
    *,
    session: Annotated[Session, Depends(get_session)],
    department: Department = Body(...)
):
    session.add(department)
    session.commit()
    session.refresh(department)
    return department


@router.post("/course", response_model=CourseRead)
def add_course(
    *,
    session: Annotated[Session, Depends(get_session)],
    course_data: CourseAdd = Body(...)
):
    course = Course.from_orm(course_data)
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.get("/attendance-log", response_model=List[AttendanceLogRead])
async def read_attendance_log(session: Session = Depends(get_session)):
    attendance_logs = session.query(AttendanceLog).all()
    return attendance_logs


@router.post("/attendance-log", response_model=AttendanceLogRead)
def add_attendance_log(
    *,
    session: Annotated[Session, Depends(get_session)],
    attendance_data: AttendanceLogCreate = Body(...)
):
    attendance_log = AttendanceLog.from_orm(attendance_data)
    session.add(attendance_log)
    session.commit()
    session.refresh(attendance_log)
    return attendance_log


@router.post("/student", response_model=StudentRead)
def add_student(
    *,
    session: Annotated[Session, Depends(get_session)],
    student_data: StudentCreate = Body(...)
):
    student = Student.from_orm(student_data)
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@router.post("/users", response_model=UserRead)
def add_user(
    *,
    session: Annotated[Session, Depends(get_session)],
    user_data: UserCreate = Body(...)
):
    user = User.from_orm(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user