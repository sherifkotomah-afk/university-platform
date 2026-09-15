from sqlalchemy import (
    Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, Text, Boolean
)
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    programme_id = Column(Integer, ForeignKey("programmes.id"))
    application_type = Column(String(20))  # Fresh, Transfer, International, Graduate
    status = Column(String(30), default="Submitted")
    # -- Ghana-specific admissions fields --
    wassce_index_number = Column(String(50))
    wassce_year = Column(Integer)
    core_english_grade = Column(String(2))
    core_maths_grade = Column(String(2))
    core_science_or_social_studies_grade = Column(String(2))
    elective_subjects = Column(JSONB)  # [{ "subject": "...", "grade": "..." }, ...] min 3
    gtec_verification_reference = Column(String(100))
    prior_qualification = Column(String(100))
    prior_institution = Column(String(255))
    prior_fgpa_or_cwa = Column(Numeric(5, 2))
    submitted_at = Column(TIMESTAMP)
    decision_at = Column(TIMESTAMP)
    decision_notes = Column(Text)


class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"))
    document_type = Column(String(50), nullable=False)
    file_url = Column(String, nullable=False)
    uploaded_at = Column(TIMESTAMP)
    verified = Column(Boolean, default=False)
