from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, Date, ForeignKey, Text
)
from app.database import Base


class Hostel(Base):
    __tablename__ = "hostels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    capacity = Column(Integer)
    gender_type = Column(String(20))


class RoomAllocation(Base):
    __tablename__ = "room_allocations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    hostel_id = Column(Integer, ForeignKey("hostels.id"))
    room_number = Column(String(20))
    academic_year = Column(String(9))
    status = Column(String(20), default="Applied")  # Applied, Allocated, Checked In, Checked Out


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    description = Column(Text)
    patron_faculty_id = Column(Integer, ForeignKey("faculty_profiles.id"))


class ClubMembership(Base):
    __tablename__ = "club_memberships"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    club_id = Column(Integer, ForeignKey("clubs.id"), primary_key=True)
    joined_at = Column(TIMESTAMP)


class LibraryItem(Base):
    __tablename__ = "library_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500))
    author = Column(String(255))
    isbn = Column(String(30))
    copies_total = Column(Integer)
    copies_available = Column(Integer)
    is_ebook = Column(Boolean, default=False)
    ebook_url = Column(String)


class LibraryLoan(Base):
    __tablename__ = "library_loans"

    id = Column(Integer, primary_key=True, index=True)
    library_item_id = Column(Integer, ForeignKey("library_items.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    borrowed_at = Column(TIMESTAMP)
    due_date = Column(Date)
    returned_at = Column(TIMESTAMP)
