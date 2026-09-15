from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StudentOut(BaseModel):
    id: int
    student_id_number: str
    programme_id: int
    current_year_level: int
    admission_year: Optional[str] = None
    status: str
    registration_hold: bool
    hold_reason: Optional[str] = None

    class Config:
        from_attributes = True


class RegisterCourseRequest(BaseModel):
    course_id: int
    academic_year: str
    semester: int


class CourseRegistrationOut(BaseModel):
    id: int
    course_id: int
    academic_year: str
    semester: int
    status: str
    registered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssessmentComponentOut(BaseModel):
    id: int
    component_type: str
    max_score: float
    score: Optional[float] = None
    weight_percent: float
    released_to_student: bool

    class Config:
        from_attributes = True


class FinalGradeOut(BaseModel):
    total_score: Optional[float] = None
    letter_grade: Optional[str] = None
    grade_point: Optional[float] = None
    appeal_status: str

    class Config:
        from_attributes = True


class CourseResultOut(BaseModel):
    course_registration_id: int
    course_code: str
    course_title: str
    credit_hours: int
    academic_year: str
    semester: int
    components: List[AssessmentComponentOut] = []
    final_grade: Optional[FinalGradeOut] = None


class TranscriptSummaryOut(BaseModel):
    grading_system: str  # 'GPA' or 'CWA'
    overall_value: float  # cumulative GPA or CWA depending on institution setting
    total_credit_hours_completed: int
    results: List[CourseResultOut]


class GradeAppealRequest(BaseModel):
    course_registration_id: int
    reason: str


class RequestTranscriptRequest(BaseModel):
    request_type: str  # 'Unofficial' or 'Official'


class TranscriptRequestOut(BaseModel):
    id: int
    request_type: str
    status: str
    requested_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None

    class Config:
        from_attributes = True
