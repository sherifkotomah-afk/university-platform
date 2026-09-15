"""
Faculty endpoints: what a lecturer sees and does for their assigned courses.

Grading integrity rule enforced here: a lecturer enters scores, but scores
are NOT visible to students (released_to_student stays False) and final
grades are NOT computed until a registrar approves them (approved_by_registrar
becomes True). This mirrors the real academic-board approval workflow and
prevents a single person from both entering and releasing grades unchecked.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.faculty import FacultyProfile, CourseAssignment
from app.models.students import CourseRegistration, AssessmentComponent, FinalGrade, Student
from app.models.lms import CourseMaterial, Assignment
from app.schemas.faculty import (
    CourseAssignmentOut, RosterEntryOut, SetAssessmentComponentRequest,
    AssessmentComponentAdminOut, SubmitFinalGradeRequest, UploadMaterialRequest,
    CreateAssignmentRequest
)
from app.core.deps import require_role
from app.core.grading import score_to_letter_and_point

router = APIRouter(prefix="/faculty", tags=["faculty"])


def _get_faculty_or_403(db: Session, current_user: User) -> FacultyProfile:
    profile = db.query(FacultyProfile).filter(FacultyProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=403, detail="No faculty profile associated with this account.")
    return profile


def _get_own_assignment_or_403(db: Session, faculty: FacultyProfile, course_assignment_id: int) -> CourseAssignment:
    assignment = db.query(CourseAssignment).filter(
        CourseAssignment.id == course_assignment_id, CourseAssignment.faculty_id == faculty.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=403, detail="This course is not assigned to you.")
    return assignment


@router.get("/me/courses", response_model=List[CourseAssignmentOut])
def my_courses(
    academic_year: str = None,
    semester: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    faculty = _get_faculty_or_403(db, current_user)
    query = db.query(CourseAssignment).filter(CourseAssignment.faculty_id == faculty.id)
    if academic_year:
        query = query.filter(CourseAssignment.academic_year == academic_year)
    if semester:
        query = query.filter(CourseAssignment.semester == semester)
    return query.all()


@router.get("/me/courses/{course_assignment_id}/roster", response_model=List[RosterEntryOut])
def course_roster(
    course_assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    faculty = _get_faculty_or_403(db, current_user)
    assignment = _get_own_assignment_or_403(db, faculty, course_assignment_id)

    registrations = (
        db.query(CourseRegistration)
        .filter(
            CourseRegistration.course_id == assignment.course_id,
            CourseRegistration.academic_year == assignment.academic_year,
            CourseRegistration.semester == assignment.semester,
            CourseRegistration.status != "Dropped",
        )
        .all()
    )

    roster = []
    for reg in registrations:
        student = db.query(Student).filter(Student.id == reg.student_id).first()
        user = student.user
        roster.append(RosterEntryOut(
            course_registration_id=reg.id,
            student_id=student.id,
            student_id_number=student.student_id_number,
            first_name=user.first_name,
            last_name=user.last_name,
            registration_status=reg.status,
        ))
    return roster


@router.post("/me/assessment-components", response_model=AssessmentComponentAdminOut, status_code=status.HTTP_201_CREATED)
def set_assessment_component(
    payload: SetAssessmentComponentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Enter/update a CAT, quiz, assignment, or exam score for one student's course registration."""
    faculty = _get_faculty_or_403(db, current_user)

    reg = db.query(CourseRegistration).filter(CourseRegistration.id == payload.course_registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Course registration not found.")

    # Confirm this lecturer actually teaches this course/semester.
    owns_it = db.query(CourseAssignment).filter(
        CourseAssignment.faculty_id == faculty.id,
        CourseAssignment.course_id == reg.course_id,
        CourseAssignment.academic_year == reg.academic_year,
        CourseAssignment.semester == reg.semester,
    ).first()
    if not owns_it:
        raise HTTPException(status_code=403, detail="You are not assigned to teach this course.")

    existing = db.query(AssessmentComponent).filter(
        AssessmentComponent.course_registration_id == payload.course_registration_id,
        AssessmentComponent.component_type == payload.component_type,
    ).first()

    if existing:
        if existing.approved_by_registrar:
            raise HTTPException(status_code=400, detail="This component was already approved by the registrar and can no longer be edited directly; submit a correction request instead.")
        existing.score = payload.score
        existing.max_score = payload.max_score
        existing.weight_percent = payload.weight_percent
        existing.entered_by = current_user.id
        existing.entered_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return existing

    component = AssessmentComponent(
        course_registration_id=payload.course_registration_id,
        component_type=payload.component_type,
        max_score=payload.max_score,
        score=payload.score,
        weight_percent=payload.weight_percent,
        entered_by=current_user.id,
        entered_at=datetime.now(timezone.utc),
    )
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


@router.get("/me/course-registrations/{course_registration_id}/components", response_model=List[AssessmentComponentAdminOut])
def list_components(
    course_registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    faculty = _get_faculty_or_403(db, current_user)
    reg = db.query(CourseRegistration).filter(CourseRegistration.id == course_registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Course registration not found.")
    owns_it = db.query(CourseAssignment).filter(
        CourseAssignment.faculty_id == faculty.id,
        CourseAssignment.course_id == reg.course_id,
        CourseAssignment.academic_year == reg.academic_year,
        CourseAssignment.semester == reg.semester,
    ).first()
    if not owns_it:
        raise HTTPException(status_code=403, detail="You are not assigned to teach this course.")
    return db.query(AssessmentComponent).filter(AssessmentComponent.course_registration_id == course_registration_id).all()


@router.post("/me/submit-final-grade", status_code=status.HTTP_202_ACCEPTED)
def submit_final_grade(
    payload: SubmitFinalGradeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """
    Lecturer submits a proposed final grade. It is NOT released to the
    student yet — it goes to 'Under Review' and waits for registrar
    approval (see admin.py). Grade point/letter grade is pre-computed here
    for the registrar's convenience but isn't final until approved.
    """
    faculty = _get_faculty_or_403(db, current_user)
    reg = db.query(CourseRegistration).filter(CourseRegistration.id == payload.course_registration_id).first()
    if not reg:
        raise HTTPException(status_code=404, detail="Course registration not found.")

    owns_it = db.query(CourseAssignment).filter(
        CourseAssignment.faculty_id == faculty.id,
        CourseAssignment.course_id == reg.course_id,
        CourseAssignment.academic_year == reg.academic_year,
        CourseAssignment.semester == reg.semester,
    ).first()
    if not owns_it:
        raise HTTPException(status_code=403, detail="You are not assigned to teach this course.")

    letter, point = score_to_letter_and_point(payload.total_score)

    final = db.query(FinalGrade).filter(FinalGrade.course_registration_id == payload.course_registration_id).first()
    if final:
        if final.total_score is not None:
            raise HTTPException(status_code=400, detail="A final grade already exists for this registration. Use the appeal/correction process instead.")
        final.total_score = payload.total_score
        final.letter_grade = letter
        final.grade_point = point
    else:
        final = FinalGrade(
            course_registration_id=payload.course_registration_id,
            total_score=payload.total_score,
            letter_grade=letter,
            grade_point=point,
        )
        db.add(final)

    db.commit()
    return {"detail": "Final grade submitted and pending registrar approval.", "letter_grade": letter, "grade_point": point}


@router.post("/me/materials", status_code=status.HTTP_201_CREATED)
def upload_material(
    payload: UploadMaterialRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    faculty = _get_faculty_or_403(db, current_user)
    _get_own_assignment_or_403(db, faculty, payload.course_assignment_id)

    material = CourseMaterial(
        course_assignment_id=payload.course_assignment_id,
        title=payload.title,
        file_url=payload.file_url,
        material_type=payload.material_type,
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return {"id": material.id, "title": material.title, "file_url": material.file_url}


@router.post("/me/assignments", status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: CreateAssignmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    faculty = _get_faculty_or_403(db, current_user)
    _get_own_assignment_or_403(db, faculty, payload.course_assignment_id)

    assignment = Assignment(
        course_assignment_id=payload.course_assignment_id,
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
        max_score=payload.max_score,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return {"id": assignment.id, "title": assignment.title, "due_at": assignment.due_at}
