from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class NewsPostOut(BaseModel):
    id: int
    title: str
    body: str
    published: bool
    published_at: Optional[datetime] = None
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class CreateNewsPostRequest(BaseModel):
    title: str
    body: str
    cover_image_url: Optional[str] = None
    published: bool = False


class EventOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class CreateEventRequest(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class StaffDirectoryOut(BaseModel):
    id: int
    title: Optional[str] = None
    office_location: Optional[str] = None
    public_email: Optional[str] = None
    photo_url: Optional[str] = None
    first_name: str
    last_name: str
    department_name: Optional[str] = None


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    channel: str
    read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    recipient_id: int
    subject: str
    body: str


class MessageOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    subject: Optional[str] = None
    body: Optional[str] = None
    sent_at: Optional[datetime] = None
    read: bool

    class Config:
        from_attributes = True


class CreateSupportTicketRequest(BaseModel):
    category: str
    subject: str
    description: str


class SupportTicketOut(BaseModel):
    id: int
    category: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HostelOut(BaseModel):
    id: int
    name: str
    capacity: Optional[int] = None
    gender_type: Optional[str] = None

    class Config:
        from_attributes = True


class ApplyHostelRequest(BaseModel):
    hostel_id: int
    academic_year: str


class RoomAllocationOut(BaseModel):
    id: int
    hostel_id: int
    room_number: Optional[str] = None
    academic_year: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class LibraryItemOut(BaseModel):
    id: int
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    copies_available: int
    is_ebook: bool
    ebook_url: Optional[str] = None

    class Config:
        from_attributes = True


class BorrowRequest(BaseModel):
    library_item_id: int
    due_date: str  # ISO date


class ClubOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True
