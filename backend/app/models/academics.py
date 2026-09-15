from sqlalchemy import (
    Column, Integer, String, Boolean, Numeric, Date, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    dean_user_id = Column(Integer, ForeignKey("users.id"))

    departments = relationship("Department", back_populates="school")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    hod_user_id = Column(Integer, ForeignKey("users.id"))

    school = relationship("School", back_populates="departments")
    programmes = relationship("Programme", back_populates="department")


class Programme(Base):
    __tablename__ = "programmes"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    level = Column(String(20), nullable=False)  # Diploma, Undergraduate, Masters, PhD, Certificate
    duration_years = Column(Numeric(3, 1), nullable=False)
    total_credit_hours = Column(Integer, nullable=False)
    accreditation_status = Column(String(50), default="Accredited")
    accreditation_expiry = Column(Date)
    description = Column(Text)

    department = relationship("Department", back_populates="programmes")
    courses = relationship("Course", back_populates="programme")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    programme_id = Column(Integer, ForeignKey("programmes.id", ondelete="CASCADE"))
    code = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    credit_hours = Column(Integer, nullable=False)
    semester_offered = Column(Integer, nullable=False)
    year_level = Column(Integer, nullable=False)
    course_type = Column(String(20), nullable=False)  # Required, Elective
    description = Column(Text)
    syllabus_url = Column(String)
    approved_by_board = Column(Boolean, default=False)

    programme = relationship("Programme", back_populates="courses")


class AcademicCalendar(Base):
    __tablename__ = "academic_calendar"

    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(9), nullable=False)
    semester = Column(Integer, nullable=False)
    registration_start = Column(Date)
    registration_end = Column(Date)
    lectures_start = Column(Date)
    lectures_end = Column(Date)
    exams_start = Column(Date)
    exams_end = Column(Date)
