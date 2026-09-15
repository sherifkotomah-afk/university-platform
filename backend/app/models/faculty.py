from sqlalchemy import (
    Column, Integer, String, Numeric, Date, Time, TIMESTAMP, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    staff_id_number = Column(String(30), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    academic_rank = Column(String(50))
    office_location = Column(String(100))
    bio = Column(Text)

    user = relationship("User", back_populates="faculty_profile")


class CourseAssignment(Base):
    __tablename__ = "course_assignments"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty_profiles.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    academic_year = Column(String(9), nullable=False)
    semester = Column(Integer, nullable=False)


class OfficeHour(Base):
    __tablename__ = "office_hours"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty_profiles.id"))
    day_of_week = Column(String(10))
    start_time = Column(Time)
    end_time = Column(Time)
    location = Column(String(100))


class AdvisingAppointment(Base):
    __tablename__ = "advising_appointments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    advisor_id = Column(Integer, ForeignKey("users.id"))
    scheduled_at = Column(TIMESTAMP, nullable=False)
    status = Column(String(20), default="Scheduled")  # Scheduled, Completed, Cancelled
    notes = Column(Text)


class ResearchPublication(Base):
    __tablename__ = "research_publications"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty_profiles.id"))
    title = Column(String(500), nullable=False)
    journal_or_venue = Column(String(255))
    publication_year = Column(Integer)
    doi_or_link = Column(String)


class ResearchGrant(Base):
    __tablename__ = "research_grants"

    id = Column(Integer, primary_key=True, index=True)
    faculty_id = Column(Integer, ForeignKey("faculty_profiles.id"))
    title = Column(String(255))
    funder = Column(String(255))
    amount = Column(Numeric(12, 2))
    start_date = Column(Date)
    end_date = Column(Date)
