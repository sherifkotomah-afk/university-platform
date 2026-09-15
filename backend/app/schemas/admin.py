from pydantic import BaseModel
from typing import Optional


class SetRegistrationHoldRequest(BaseModel):
    student_id: int
    hold: bool
    reason: Optional[str] = None


class ApproveTranscriptRequest(BaseModel):
    status: str  # 'Approved' or 'Rejected'


class CreateUserRequest(BaseModel):
    """For admin-created accounts: faculty, admin, registrar, finance staff."""
    email: str
    password: str
    role: str  # faculty, admin, registrar, finance
    first_name: str
    last_name: str
    phone: Optional[str] = None


class CreateFacultyProfileRequest(BaseModel):
    user_id: int
    staff_id_number: str
    department_id: int
    academic_rank: Optional[str] = None
    office_location: Optional[str] = None
    bio: Optional[str] = None


class AssignCourseToFacultyRequest(BaseModel):
    faculty_id: int
    course_id: int
    academic_year: str
    semester: int
