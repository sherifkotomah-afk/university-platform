from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, text
)
from sqlalchemy.orm import relationship
from app.database import Base


class InstitutionSettings(Base):
    """
    White-label config. One row per deployed institution.
    Changing this table's values rebrands the entire platform
    without touching code.
    """
    __tablename__ = "institution_settings"

    id = Column(Integer, primary_key=True, index=True)
    institution_name = Column(String(255), nullable=False)
    short_code = Column(String(20), nullable=False)
    logo_url = Column(String)
    primary_color = Column(String(7), default="#1a1a2e")
    secondary_color = Column(String(7), default="#ffffff")
    grading_system = Column(String(10), nullable=False, default="GPA")  # 'GPA' or 'CWA'
    academic_year = Column(String(9), nullable=False)
    current_semester = Column(Integer, nullable=False, default=1)
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    address = Column(String)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # applicant, student, faculty, admin, registrar, finance
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=True)
    last_login = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=text("now()"))

    student_profile = relationship("Student", back_populates="user", uselist=False)
    faculty_profile = relationship("FacultyProfile", back_populates="user", uselist=False)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    refresh_token_hash = Column(String(255), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
