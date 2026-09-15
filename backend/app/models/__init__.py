"""
Import every model here so that Base.metadata is fully populated —
this matters for Alembic autogenerate and for any script that calls
Base.metadata.create_all().
"""
from app.models.core import InstitutionSettings, User, UserSession
from app.models.academics import School, Department, Programme, Course, AcademicCalendar
from app.models.admissions import Application, ApplicationDocument
from app.models.students import (
    Student, CourseRegistration, AssessmentComponent, FinalGrade, TranscriptRequest
)
from app.models.fees import (
    FeeItem, StudentFeeInvoice, InvoiceLineItem, Payment, PaymentPlan,
    ScholarshipFinancialAid
)
from app.models.faculty import (
    FacultyProfile, CourseAssignment, OfficeHour, AdvisingAppointment,
    ResearchPublication, ResearchGrant
)
from app.models.student_life import (
    Hostel, RoomAllocation, Club, ClubMembership, LibraryItem, LibraryLoan
)
from app.models.lms import CourseMaterial, Assignment, AssignmentSubmission, DiscussionPost
from app.models.misc import (
    Notification, Message, SupportTicket, NewsPost, Event, StaffDirectory, AuditLog
)

__all__ = [
    "InstitutionSettings", "User", "UserSession",
    "School", "Department", "Programme", "Course", "AcademicCalendar",
    "Application", "ApplicationDocument",
    "Student", "CourseRegistration", "AssessmentComponent", "FinalGrade", "TranscriptRequest",
    "FeeItem", "StudentFeeInvoice", "InvoiceLineItem", "Payment", "PaymentPlan",
    "ScholarshipFinancialAid",
    "FacultyProfile", "CourseAssignment", "OfficeHour", "AdvisingAppointment",
    "ResearchPublication", "ResearchGrant",
    "Hostel", "RoomAllocation", "Club", "ClubMembership", "LibraryItem", "LibraryLoan",
    "CourseMaterial", "Assignment", "AssignmentSubmission", "DiscussionPost",
    "Notification", "Message", "SupportTicket", "NewsPost", "Event", "StaffDirectory", "AuditLog",
]
