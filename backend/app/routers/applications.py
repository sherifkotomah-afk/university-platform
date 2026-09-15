"""
Applicant portal endpoints.

Flow:
1. Applicant (already registered via /auth/register) submits an application.
2. Applicant uploads supporting documents against that application.
3. Admin/registrar reviews and moves status forward (Under Review -> Offer
   Made -> Accepted/Rejected). See admin.py for the decision endpoints.
4. Once status = 'Enrolled', a Student record is created and the user's
   role is upgraded from 'applicant' to 'student' — this is the one
   moment a user's role changes, and it only happens server-side here,
   never by a request the user controls.
"""
import random
import string
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.admissions import Application, ApplicationDocument
from app.models.academics import Programme
from app.models.students import Student
from app.schemas.applications import (
    SubmitApplicationRequest, ApplicationOut, ApplicationDocumentOut,
    UploadDocumentRequest, DecisionRequest
)
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def submit_application(
    payload: SubmitApplicationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("applicant")),
):
    programme = db.query(Programme).filter(Programme.id == payload.programme_id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found.")

    application = Application(
        user_id=current_user.id,
        programme_id=payload.programme_id,
        application_type=payload.application_type,
        status="Submitted",
        wassce_index_number=payload.wassce_index_number,
        wassce_year=payload.wassce_year,
        core_english_grade=payload.core_english_grade,
        core_maths_grade=payload.core_maths_grade,
        core_science_or_social_studies_grade=payload.core_science_or_social_studies_grade,
        elective_subjects=[e.model_dump() for e in payload.elective_subjects] if payload.elective_subjects else None,
        gtec_verification_reference=payload.gtec_verification_reference,
        prior_qualification=payload.prior_qualification,
        prior_institution=payload.prior_institution,
        prior_fgpa_or_cwa=payload.prior_fgpa_or_cwa,
        submitted_at=datetime.now(timezone.utc),
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/mine", response_model=List[ApplicationOut])
def my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Application).filter(Application.user_id == current_user.id).all()


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    if application.user_id != current_user.id and current_user.role not in ("admin", "registrar"):
        raise HTTPException(status_code=403, detail="Not authorized to view this application.")
    return application


@router.post("/{application_id}/documents", response_model=ApplicationDocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    application_id: int,
    payload: UploadDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    if application.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this application.")

    doc = ApplicationDocument(
        application_id=application_id,
        document_type=payload.document_type,
        file_url=payload.file_url,
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{application_id}/documents", response_model=List[ApplicationDocumentOut])
def list_documents(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    if application.user_id != current_user.id and current_user.role not in ("admin", "registrar"):
        raise HTTPException(status_code=403, detail="Not authorized to view these documents.")
    return db.query(ApplicationDocument).filter(ApplicationDocument.application_id == application_id).all()


# ---------------- Admin/Registrar decision workflow ----------------

def _generate_student_id_number(db: Session, admission_year: str) -> str:
    """e.g. 2026-000123 — simple, collision-checked sequential-ish generator."""
    while True:
        candidate = f"{admission_year[:4]}-{random.randint(100000, 999999)}"
        exists = db.query(Student).filter(Student.student_id_number == candidate).first()
        if not exists:
            return candidate


@router.patch("/{application_id}/decision", response_model=ApplicationOut,
              dependencies=[Depends(require_role("admin", "registrar"))])
def decide_application(
    application_id: int,
    payload: DecisionRequest,
    db: Session = Depends(get_db),
):
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    application.status = payload.status
    application.decision_notes = payload.decision_notes
    application.decision_at = datetime.now(timezone.utc)

    if payload.status == "Enrolled":
        applicant_user = db.query(User).filter(User.id == application.user_id).first()
        existing_student = db.query(Student).filter(Student.user_id == applicant_user.id).first()
        if not existing_student:
            admission_year = str(datetime.now(timezone.utc).year)
            student = Student(
                user_id=applicant_user.id,
                student_id_number=_generate_student_id_number(db, admission_year),
                programme_id=application.programme_id,
                current_year_level=1,
                admission_year=admission_year,
                status="Active",
            )
            db.add(student)
            applicant_user.role = "student"

    db.commit()
    db.refresh(application)
    return application


@router.get("", response_model=List[ApplicationOut],
            dependencies=[Depends(require_role("admin", "registrar"))])
def list_all_applications(status_filter: str = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    return query.order_by(Application.submitted_at.desc()).all()
