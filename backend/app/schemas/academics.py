from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class CourseOut(BaseModel):
    id: int
    code: str
    title: str
    credit_hours: int
    semester_offered: int
    year_level: int
    course_type: str
    description: Optional[str] = None
    syllabus_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProgrammeOut(BaseModel):
    id: int
    name: str
    level: str
    duration_years: float
    total_credit_hours: int
    accreditation_status: str
    description: Optional[str] = None
    courses: List[CourseOut] = []

    class Config:
        from_attributes = True


class DepartmentOut(BaseModel):
    id: int
    name: str
    programmes: List[ProgrammeOut] = []

    class Config:
        from_attributes = True


class SchoolOut(BaseModel):
    id: int
    name: str
    departments: List[DepartmentOut] = []

    class Config:
        from_attributes = True


class AcademicCalendarOut(BaseModel):
    academic_year: str
    semester: int
    registration_start: Optional[date] = None
    registration_end: Optional[date] = None
    lectures_start: Optional[date] = None
    lectures_end: Optional[date] = None
    exams_start: Optional[date] = None
    exams_end: Optional[date] = None

    class Config:
        from_attributes = True
