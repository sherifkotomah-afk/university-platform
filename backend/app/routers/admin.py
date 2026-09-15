"""
Admin/registrar back-office endpoints.

This is where the "second pair of eyes" on grades lives: a registrar
approves assessment components and final grades before they ever become
visible to a student. It's also where non-self-service accounts (faculty,
admin, registrar, finance) get created — these roles are never created
through public sign-up.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.students import Student, AssessmentComponent, FinalGrade, TranscriptRequest
from app.models.faculty import FacultyProfile, CourseAssignment
from app.core.security import hash_password
from app.core.deps import require_role
from app.schemas.admin import (
    SetRegistrationHoldRequest, ApproveTranscriptRequest, CreateUserRequest,
    CreateFacultyProfileRequest, AssignCourseToFacultyRequest
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------- Grade approval workflow ----------------

@router.patch("/assessment-components/{component_id}/approve",
              dependencies=[Depends(require_role("admin", "registrar"))])
def approve_assessment_component(component_id: int, db: Session = Depends(get_db)):
    component = db.query(AssessmentComponent).filter(AssessmentComponent.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Assessment component not found.")
    component.approved_by_registrar = True
    component.released_to_student = True
    db.commit()
    return {"detail": "Component approved and released to student."}


@router.patch("/final-grades/{course_registration_id}/approve",
              dependencies=[Depends(require_role("admin", "registrar"))])
def approve_final_grade(course_registration_id: int, db: Session = Depends(get_db)):
    final = db.query(FinalGrade).filter(FinalGrade.course_registration_id == course_registration_id).first()
    if not final or final.total_score is None:
        raise HTTPException(status_code=404, detail="No submitted final grade found for this course registration.")
    # Approval = the grade becomes visible via /students/me/results and counts toward the transcript.
    # (We don't add a separate "approved" flag on FinalGrade in the schema; approval is represented
    # by also approving/releasing the linked 'Exam' assessment component, keeping one source of truth.)
    exam_component = db.query(AssessmentComponent).filter(
        AssessmentComponent.course_registration_id == course_registration_id,
        AssessmentComponent.component_type == "Exam",
    ).first()
    if exam_component:
        exam_component.approved_by_registrar = True
        exam_component.released_to_student = True
    db.commit()
    return {"detail": "Final grade approved and released to student.", "letter_grade": final.letter_grade}


@router.get("/final-grades/pending-approval", dependencies=[Depends(require_role("admin", "registrar"))])
def list_pending_final_grades(db: Session = Depends(get_db)):
    pending = db.query(FinalGrade).filter(FinalGrade.total_score.isnot(None)).all()
    result = []
    for f in pending:
        exam = db.query(AssessmentComponent).filter(
            AssessmentComponent.course_registration_id == f.course_registration_id,
            AssessmentComponent.component_type == "Exam",
        ).first()
        if not exam or not exam.approved_by_registrar:
            result.append({
                "course_registration_id": f.course_registration_id,
                "total_score": float(f.total_score),
                "letter_grade": f.letter_grade,
                "grade_point": float(f.grade_point) if f.grade_point is not None else None,
            })
    return result


# ---------------- Registration holds ----------------

@router.patch("/students/registration-hold", dependencies=[Depends(require_role("admin", "registrar", "finance"))])
def set_registration_hold(payload: SetRegistrationHoldRequest, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    student.registration_hold = payload.hold
    student.hold_reason = payload.reason if payload.hold else None
    db.commit()
    return {"detail": f"Registration hold {'placed' if payload.hold else 'lifted'}."}


# ---------------- Transcript request approval ----------------

@router.patch("/transcript-requests/{request_id}", dependencies=[Depends(require_role("admin", "registrar"))])
def approve_transcript_request(request_id: int, payload: ApproveTranscriptRequest, db: Session = Depends(get_db),
                                current_user: User = Depends(require_role("admin", "registrar"))):
    req = db.query(TranscriptRequest).filter(TranscriptRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Transcript request not found.")
    req.status = payload.status
    req.approved_by = current_user.id
    if payload.status == "Approved":
        req.status = "Issued"
        req.issued_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": f"Transcript request marked as {req.status}."}


@router.get("/transcript-requests", dependencies=[Depends(require_role("admin", "registrar"))])
def list_transcript_requests(status_filter: str = None, db: Session = Depends(get_db)):
    query = db.query(TranscriptRequest)
    if status_filter:
        query = query.filter(TranscriptRequest.status == status_filter)
    return query.order_by(TranscriptRequest.requested_at.desc()).all()


# ---------------- Staff/account management ----------------

@router.post("/users", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
def create_staff_user(payload: CreateUserRequest, db: Session = Depends(get_db)):
    if payload.role not in ("faculty", "admin", "registrar", "finance"):
        raise HTTPException(status_code=400, detail="Role must be one of: faculty, admin, registrar, finance.")
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        must_change_password=True,  # staff accounts are issued a temp password, must change on first login
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "role": user.role}


@router.post("/faculty-profiles", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
def create_faculty_profile(payload: CreateFacultyProfileRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id, User.role == "faculty").first()
    if not user:
        raise HTTPException(status_code=404, detail="Faculty user not found (create the user with role='faculty' first).")

    existing = db.query(FacultyProfile).filter(FacultyProfile.user_id == payload.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Faculty profile already exists for this user.")

    profile = FacultyProfile(
        user_id=payload.user_id,
        staff_id_number=payload.staff_id_number,
        department_id=payload.department_id,
        academic_rank=payload.academic_rank,
        office_location=payload.office_location,
        bio=payload.bio,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id, "staff_id_number": profile.staff_id_number}


@router.post("/course-assignments", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("admin"))])
def assign_course_to_faculty(payload: AssignCourseToFacultyRequest, db: Session = Depends(get_db)):
    faculty = db.query(FacultyProfile).filter(FacultyProfile.id == payload.faculty_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")

    assignment = CourseAssignment(
        faculty_id=payload.faculty_id,
        course_id=payload.course_id,
        academic_year=payload.academic_year,
        semester=payload.semester,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"id": assignment.id}
