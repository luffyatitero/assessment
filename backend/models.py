from typing import List, ClassVar, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

from sqlalchemy.orm import relationship


class BaseModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    submitted_by: str
    updated_at: str | None = Field(default_factory=datetime.now)


class User(BaseModel, table=True):
    user_type: str
    full_name: str
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    password: str
    student: ClassVar[Optional[List["Student"]]] = relationship(
        "Student", back_populates="user"
    )

class UserCreate(SQLModel):
    user_type: str
    full_name: str
    username: str
    email: str
    password: str
    submitted_by: str

class UserRead(BaseModel):
    user_type: str
    full_name: str
    email: str


class Department(BaseModel, table=True):
    department_name: str
    courses: ClassVar[Optional[List["Course"]]] = relationship(
        "Course", back_populates="department"
    )
    students: ClassVar[Optional[List["Student"]]] = relationship(
        "Student", back_populates="department"
    )

class DepartmentRead(SQLModel):
    id: int
    department_name: str
    submitted_by: str
    updated_at: str

class Course(BaseModel, table=True):
    course_name: str
    department_id: int = Field(foreign_key="department.id")
    semester: str
    class_id: int = Field(index=True)
    lecture_hours: int
    department: ClassVar[Optional["Department"]] = relationship(
        Department, back_populates="courses"
    )
    attendance_logs: ClassVar[Optional["AttendanceLog"]] = relationship(
        "AttendanceLog", back_populates="course"
    )

class CourseAdd(SQLModel):
    submitted_by: str
    course_name: str
    department_id: int
    semester: str
    class_id: int
    lecture_hours: int

class CourseRead(BaseModel):
    course_name: str
    department: DepartmentRead
    semester: str
    class_id: int
    lecture_hours: int

class Student(BaseModel, table=True):
    user_id: int = Field(foreign_key="user.id")
    department_id: int = Field(foreign_key="department.id")
    class_id: int = Field(index=True)
    attendance_logs: ClassVar[Optional["AttendanceLog"]] = relationship(
        "AttendanceLog", back_populates="student"
    )
    user: ClassVar[Optional["User"]] = relationship(
        "User", back_populates="student"
    )
    department: ClassVar[Optional["Department"]] = relationship(
        "Department", back_populates="students"
    )

class StudentCreate(SQLModel):
    user_id: int
    department_id: int
    class_id: int
    submitted_by: str

class StudentRead(SQLModel):
    id: int
    submitted_by: str
    updated_at: datetime
    class_id: int
    user: UserRead
    department: DepartmentRead


class AttendanceLog(BaseModel, table=True):
    student_id: int = Field(foreign_key="student.id")
    course_id: int = Field(foreign_key="course.id")
    present: bool = Field(default=False)
    student: ClassVar[Optional["Student"]] = relationship(
        Student, back_populates="attendance_logs"
    )
    course: ClassVar[Optional["Course"]] = relationship(
        Course, back_populates="attendance_logs"
    )

class AttendanceLogRead(BaseModel):
    student: StudentRead
    course: CourseRead
    present: bool

class AttendanceLogCreate(SQLModel):
    submitted_by: str
    student_id: int
    course_id: int
    present: bool
