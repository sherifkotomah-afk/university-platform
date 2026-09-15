from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CourseAssignmentOut(BaseModel):
    id: int
    course_id: int
    academic_year: str
    semester: int

    class Config:
        from_attributes = True


class RosterEntryOut(BaseModel):
    course_registration_id: int
    student_id: int
    student_id_number: str
    first_name: str
    last_name: str
    registration_status: str


class SetAssessmentComponentRequest(BaseModel):
    course_registration_id: int
    component_type: str  # 'CAT1','CAT2','Assignment','Exam'
    max_score: float
    score: float
    weight_percent: float


class AssessmentComponentAdminOut(BaseModel):
    id: int
    course_registration_id: int
    component_type: str
    max_score: float
    score: Optional[float] = None
    weight_percent: float
    approved_by_registrar: bool
    released_to_student: bool

    class Config:
        from_attributes = True


class SubmitFinalGradeRequest(BaseModel):
    course_registration_id: int
    total_score: float


class UploadMaterialRequest(BaseModel):
    course_assignment_id: int
    title: str
    file_url: str
    material_type: str  # 'Slide','Note','Recording','Reading'


class CreateAssignmentRequest(BaseModel):
    course_assignment_id: int
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    max_score: float
