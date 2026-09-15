from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255))
    body = Column(Text)
    channel = Column(String(20), default="in_app")  # in_app, email, sms
    read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(255))
    body = Column(Text)
    sent_at = Column(TIMESTAMP)
    read = Column(Boolean, default=False)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String(50))  # IT, Registrar, Finance, Housing
    subject = Column(String(255))
    description = Column(Text)
    status = Column(String(20), default="Open")  # Open, In Progress, Resolved, Closed
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP)
    resolved_at = Column(TIMESTAMP)


class NewsPost(Base):
    __tablename__ = "news_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    published = Column(Boolean, default=False)
    published_at = Column(TIMESTAMP)
    cover_image_url = Column(String)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)


class StaffDirectory(Base):
    __tablename__ = "staff_directory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))
    office_location = Column(String(100))
    public_email = Column(String(255))
    photo_url = Column(String)


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(JSONB)
    created_at = Column(TIMESTAMP)
