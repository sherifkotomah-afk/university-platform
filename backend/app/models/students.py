from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, TIMESTAMP, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    student_id_number = Column(String(30), unique=True, nullable=False)
    programme_id = Column(Integer, ForeignKey("programmes.id"))
    current_year_level = Column(Integer, default=1)
    admission_year = Column(String(9))
    status = Column(String(20), default="Active")  # Active, On Leave, Withdrawn, Dismissed, Graduated
    registration_hold = Column(Boolean, default=False)
    hold_reason = Column(Text)

    user = relationship("User", back_populates="student_profile")


class CourseRegistration(Base):
    __tablename__ = "course_registrations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    academic_year = Column(String(9), nullable=False)
    semester = Column(Integer, nullable=False)
    status = Column(String(20), default="Registered")  # Registered, Waitlisted, Dropped, Completed
    registered_at = Column(TIMESTAMP)


class AssessmentComponent(Base):
    __tablename__ = "assessment_components"

    id = Column(Integer, primary_key=True, index=True)
    course_registration_id = Column(Integer, ForeignKey("course_registrations.id", ondelete="CASCADE"))
    component_type = Column(String(30), nullable=False)  # CAT1, CAT2, Assignment, Exam
    max_score = Column(Numeric(5, 2), nullable=False)
    score = Column(Numeric(5, 2))
    weight_percent = Column(Numeric(5, 2), nullable=False)
    entered_by = Column(Integer, ForeignKey("users.id"))
    entered_at = Column(TIMESTAMP)
    approved_by_registrar = Column(Boolean, default=False)
    released_to_student = Column(Boolean, default=False)


class FinalGrade(Base):
    __tablename__ = "final_grades"

    id = Column(Integer, primary_key=True, index=True)
    course_registration_id = Column(Integer, ForeignKey("course_registrations.id", ondelete="CASCADE"), unique=True)
    total_score = Column(Numeric(5, 2))
    letter_grade = Column(String(2))
    grade_point = Column(Numeric(3, 2))
    is_retake = Column(Boolean, default=False)
    appeal_status = Column(String(20), default="None")  # None, Requested, Under Review, Resolved


class TranscriptRequest(Base):
    __tablename__ = "transcript_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    request_type = Column(String(20))  # Unofficial, Official
    status = Column(String(20), default="Pending")  # Pending, Approved, Issued, Rejected
    requested_at = Column(TIMESTAMP)
    issued_at = Column(TIMESTAMP)
    approved_by = Column(Integer, ForeignKey("users.id"))
