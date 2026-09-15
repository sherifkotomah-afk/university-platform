from sqlalchemy import (
    Column, Integer, String, Numeric, TIMESTAMP, ForeignKey, Text
)
from app.database import Base


class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id = Column(Integer, primary_key=True, index=True)
    course_assignment_id = Column(Integer, ForeignKey("course_assignments.id", ondelete="CASCADE"))
    title = Column(String(255))
    file_url = Column(String)
    material_type = Column(String(30))  # Slide, Note, Recording, Reading
    uploaded_at = Column(TIMESTAMP)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    course_assignment_id = Column(Integer, ForeignKey("course_assignments.id", ondelete="CASCADE"))
    title = Column(String(255))
    description = Column(Text)
    due_at = Column(TIMESTAMP)
    max_score = Column(Numeric(5, 2))


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"))
    student_id = Column(Integer, ForeignKey("students.id"))
    file_url = Column(String)
    submitted_at = Column(TIMESTAMP)
    score = Column(Numeric(5, 2))
    feedback = Column(Text)


class DiscussionPost(Base):
    __tablename__ = "discussion_posts"

    id = Column(Integer, primary_key=True, index=True)
    course_assignment_id = Column(Integer, ForeignKey("course_assignments.id", ondelete="CASCADE"))
    author_user_id = Column(Integer, ForeignKey("users.id"))
    parent_post_id = Column(Integer, ForeignKey("discussion_posts.id"))
    content = Column(Text, nullable=False)
    posted_at = Column(TIMESTAMP)
