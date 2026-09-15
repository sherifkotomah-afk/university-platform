"""
Student academic endpoints: course registration, viewing results, and
transcript generation. Registration holds (per Ghanaian academic policy —
an unregistered/indebted student can be barred from registering for
subsequent courses or getting a transcript) are enforced here, not just
displayed as a warning.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.students import (
    Student, CourseRegistration, AssessmentComponent, FinalGrade, TranscriptRequest
)
from app.models.academics import Course
from app.models.core import InstitutionSettings
from app.schemas.students import (
    StudentOut, RegisterCourseRequest, CourseRegistrationOut, CourseResultOut,
    AssessmentComponentOut, FinalGradeOut, TranscriptSummaryOut, GradeAppealRequest,
    RequestTranscriptRequest, TranscriptRequestOut
)
from app.core.deps import get_current_user, require_role
from app.core.grading import score_to_letter_and_point, compute_cumulative

router = APIRouter(prefix="/students", tags=["students"])


def _get_student_or_403(db: Session, current_user: User) -> Student:
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=403, detail="No student record associated with this account.")
    return student


@router.get("/me", response_model=StudentOut)
def get_my_student_profile(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    return _get_student_or_403(db, current_user)


@router.post("/me/register-course", response_model=CourseRegistrationOut, status_code=status.HTTP_201_CREATED)
def register_course(
    payload: RegisterCourseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    student = _get_student_or_403(db, current_user)

    if student.registration_hold:
        raise HTTPException(
            status_code=403,
            detail=f"Registration is blocked: {student.hold_reason or 'a hold is on your account. Contact the registrar/finance office.'}",
        )

    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")

    existing = (
        db.query(CourseRegistration)
        .filter(
            CourseRegistration.student_id == student.id,
            CourseRegistration.course_id == payload.course_id,
            CourseRegistration.academic_year == payload.academic_year,
            CourseRegistration.semester == payload.semester,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this course this semester.")

    registration = CourseRegistration(
        student_id=student.id,
        course_id=payload.course_id,
        academic_year=payload.academic_year,
        semester=payload.semester,
        status="Registered",
        registered_at=datetime.now(timezone.utc),
    )
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration


@router.get("/me/registrations", response_model=List[CourseRegistrationOut])
def my_registrations(
    academic_year: str = None,
    semester: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    student = _get_student_or_403(db, current_user)
    query = db.query(CourseRegistration).filter(CourseRegistration.student_id == student.id)
    if academic_year:
        query = query.filter(CourseRegistration.academic_year == academic_year)
    if semester:
        query = query.filter(CourseRegistration.semester == semester)
    return query.all()


@router.delete("/me/registrations/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
def drop_course(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    student = _get_student_or_403(db, current_user)
    reg = db.query(CourseRegistration).filter(
        CourseRegistration.id == registration_id, CourseRegistration.student_id == student.id
    ).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found.")
    reg.status = "Dropped"
    db.commit()


def _build_course_result(db: Session, reg: CourseRegistration) -> CourseResultOut:
    course = db.query(Course).filter(Course.id == reg.course_id).first()
    components = db.query(AssessmentComponent).filter(
        AssessmentComponent.course_registration_id == reg.id
    ).all()
    final = db.query(FinalGrade).filter(FinalGrade.course_registration_id == reg.id).first()

    # Only show components/final grades that have actually been released to the student.
    visible_components = [c for c in components if c.released_to_student]

    return CourseResultOut(
        course_registration_id=reg.id,
        course_code=course.code,
        course_title=course.title,
        credit_hours=course.credit_hours,
        academic_year=reg.academic_year,
        semester=reg.semester,
        components=[AssessmentComponentOut.model_validate(c) for c in visible_components],
        final_grade=FinalGradeOut.model_validate(final) if final and final.total_score is not None else None,
    )


@router.get("/me/results", response_model=List[CourseResultOut])
def my_results(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    registrations = db.query(CourseRegistration).filter(
        CourseRegistration.student_id == student.id, CourseRegistration.status != "Dropped"
    ).all()
    return [_build_course_result(db, reg) for reg in registrations]


@router.get("/me/transcript", response_model=TranscriptSummaryOut)
def my_transcript(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    settings_row = db.query(InstitutionSettings).first()
    grading_system = settings_row.grading_system if settings_row else "GPA"

    registrations = db.query(CourseRegistration).filter(
        CourseRegistration.student_id == student.id, CourseRegistration.status != "Dropped"
    ).all()

    results = []
    calc_rows = []
    for reg in registrations:
        result = _build_course_result(db, reg)
        results.append(result)
        if result.final_grade and result.final_grade.total_score is not None:
            calc_rows.append({
                "score": result.final_grade.total_score,
                "grade_point": result.final_grade.grade_point or 0.0,
                "credit_hours": result.credit_hours,
            })

    overall_value, total_credits = compute_cumulative(grading_system, calc_rows)

    return TranscriptSummaryOut(
        grading_system=grading_system,
        overall_value=overall_value or 0.0,
        total_credit_hours_completed=total_credits,
        results=results,
    )


@router.post("/me/grade-appeals", status_code=status.HTTP_204_NO_CONTENT)
def request_grade_appeal(
    payload: GradeAppealRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    student = _get_student_or_403(db, current_user)
    reg = db.query(CourseRegistration).filter(
        CourseRegistration.id == payload.course_registration_id, CourseRegistration.student_id == student.id
    ).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Course registration not found.")

    final = db.query(FinalGrade).filter(FinalGrade.course_registration_id == reg.id).first()
    if not final:
        raise HTTPException(status_code=400, detail="No final grade exists yet for this course.")

    final.appeal_status = "Requested"
    db.commit()


@router.post("/me/transcript-requests", response_model=TranscriptRequestOut, status_code=status.HTTP_201_CREATED)
def request_transcript(
    payload: RequestTranscriptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    student = _get_student_or_403(db, current_user)
    if student.registration_hold:
        raise HTTPException(
            status_code=403,
            detail=f"Transcript requests are blocked: {student.hold_reason or 'a hold is on your account.'}",
        )

    request_row = TranscriptRequest(
        student_id=student.id,
        request_type=payload.request_type,
        status="Pending",
        requested_at=datetime.now(timezone.utc),
    )
    db.add(request_row)
    db.commit()
    db.refresh(request_row)
    return request_row


@router.get("/me/transcript-requests", response_model=List[TranscriptRequestOut])
def my_transcript_requests(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    return db.query(TranscriptRequest).filter(TranscriptRequest.student_id == student.id).all()
