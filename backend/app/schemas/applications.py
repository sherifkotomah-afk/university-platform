from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ElectiveSubject(BaseModel):
    subject: str
    grade: str


class SubmitApplicationRequest(BaseModel):
    programme_id: int
    application_type: str = Field(pattern="^(Fresh|Transfer|International|Graduate)$")
    wassce_index_number: Optional[str] = None
    wassce_year: Optional[int] = None
    core_english_grade: Optional[str] = None
    core_maths_grade: Optional[str] = None
    core_science_or_social_studies_grade: Optional[str] = None
    elective_subjects: Optional[List[ElectiveSubject]] = None
    gtec_verification_reference: Optional[str] = None
    prior_qualification: Optional[str] = None
    prior_institution: Optional[str] = None
    prior_fgpa_or_cwa: Optional[float] = None


class ApplicationOut(BaseModel):
    id: int
    programme_id: int
    application_type: Optional[str]
    status: str
    wassce_index_number: Optional[str] = None
    submitted_at: Optional[datetime] = None
    decision_at: Optional[datetime] = None
    decision_notes: Optional[str] = None

    class Config:
        from_attributes = True


class ApplicationDocumentOut(BaseModel):
    id: int
    document_type: str
    file_url: str
    verified: bool
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UploadDocumentRequest(BaseModel):
    document_type: str  # e.g. 'WASSCE Result Slip', 'Passport Photo', 'Transcript', 'Essay'
    file_url: str        # frontend uploads to storage first (e.g. Supabase Storage), then sends the URL here


class DecisionRequest(BaseModel):
    """Used by admin/registrar to record a decision on an application."""
    status: str = Field(pattern="^(Under Review|Offer Made|Accepted|Rejected|Enrolled)$")
    decision_notes: Optional[str] = None
