"""
Public academics endpoints — power the public website's Academics section.
No authentication required; this is public marketing/catalog information.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.academics import School, Department, Programme, Course, AcademicCalendar
from app.schemas.academics import SchoolOut, ProgrammeOut, CourseOut, AcademicCalendarOut

router = APIRouter(prefix="/academics", tags=["academics"])


@router.get("/schools", response_model=List[SchoolOut])
def list_schools(db: Session = Depends(get_db)):
    """Full tree: schools -> departments -> programmes -> courses, for the Academics nav."""
    return (
        db.query(School)
        .options(
            joinedload(School.departments)
            .joinedload(Department.programmes)
            .joinedload(Programme.courses)
        )
        .all()
    )


@router.get("/programmes", response_model=List[ProgrammeOut])
def list_programmes(level: str = None, db: Session = Depends(get_db)):
    """Optionally filter by level: Diploma, Undergraduate, Masters, PhD, Certificate."""
    query = db.query(Programme).options(joinedload(Programme.courses))
    if level:
        query = query.filter(Programme.level == level)
    return query.all()


@router.get("/programmes/{programme_id}", response_model=ProgrammeOut)
def get_programme(programme_id: int, db: Session = Depends(get_db)):
    programme = (
        db.query(Programme)
        .options(joinedload(Programme.courses))
        .filter(Programme.id == programme_id)
        .first()
    )
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found.")
    return programme


@router.get("/courses/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    return course


@router.get("/calendar", response_model=List[AcademicCalendarOut])
def get_calendar(academic_year: str = None, db: Session = Depends(get_db)):
    query = db.query(AcademicCalendar)
    if academic_year:
        query = query.filter(AcademicCalendar.academic_year == academic_year)
    return query.order_by(AcademicCalendar.academic_year, AcademicCalendar.semester).all()
