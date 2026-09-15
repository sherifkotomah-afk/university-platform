from datetime import datetime, timezone, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.students import Student
from app.models.student_life import Hostel, RoomAllocation, LibraryItem, LibraryLoan, Club, ClubMembership
from app.schemas.campus import (
    HostelOut, ApplyHostelRequest, RoomAllocationOut, LibraryItemOut, BorrowRequest, ClubOut
)
from app.core.deps import require_role

router = APIRouter(prefix="/campus", tags=["campus"])


def _get_student_or_403(db: Session, current_user: User) -> Student:
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=403, detail="No student record associated with this account.")
    return student


# ---------------- Hostels ----------------

@router.get("/hostels", response_model=List[HostelOut])
def list_hostels(db: Session = Depends(get_db)):
    return db.query(Hostel).all()


@router.post("/hostels/apply", response_model=RoomAllocationOut, status_code=status.HTTP_201_CREATED)
def apply_for_hostel(payload: ApplyHostelRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    hostel = db.query(Hostel).filter(Hostel.id == payload.hostel_id).first()
    if not hostel:
        raise HTTPException(status_code=404, detail="Hostel not found.")

    allocation = RoomAllocation(
        student_id=student.id,
        hostel_id=payload.hostel_id,
        academic_year=payload.academic_year,
        status="Applied",
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    return allocation


@router.get("/hostels/my-allocation", response_model=List[RoomAllocationOut])
def my_hostel_allocation(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    return db.query(RoomAllocation).filter(RoomAllocation.student_id == student.id).all()


# ---------------- Library ----------------

@router.get("/library", response_model=List[LibraryItemOut])
def search_library(q: str = None, db: Session = Depends(get_db)):
    query = db.query(LibraryItem)
    if q:
        query = query.filter(LibraryItem.title.ilike(f"%{q}%"))
    return query.limit(50).all()


@router.post("/library/borrow", status_code=status.HTTP_201_CREATED)
def borrow_item(payload: BorrowRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    item = db.query(LibraryItem).filter(LibraryItem.id == payload.library_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found.")
    if item.is_ebook:
        raise HTTPException(status_code=400, detail="This is a digital item; access it directly via ebook_url, no borrowing needed.")
    if item.copies_available <= 0:
        raise HTTPException(status_code=400, detail="No copies currently available.")

    loan = LibraryLoan(
        library_item_id=item.id,
        student_id=student.id,
        borrowed_at=datetime.now(timezone.utc),
        due_date=date.fromisoformat(payload.due_date),
    )
    item.copies_available -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return {"id": loan.id, "due_date": str(loan.due_date)}


@router.post("/library/loans/{loan_id}/return", status_code=status.HTTP_204_NO_CONTENT)
def return_item(loan_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    loan = db.query(LibraryLoan).filter(LibraryLoan.id == loan_id, LibraryLoan.student_id == student.id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found.")
    if loan.returned_at:
        raise HTTPException(status_code=400, detail="Already returned.")
    loan.returned_at = datetime.now(timezone.utc)
    item = db.query(LibraryItem).filter(LibraryItem.id == loan.library_item_id).first()
    item.copies_available += 1
    db.commit()


# ---------------- Clubs ----------------

@router.get("/clubs", response_model=List[ClubOut])
def list_clubs(db: Session = Depends(get_db)):
    return db.query(Club).all()


@router.post("/clubs/{club_id}/join", status_code=status.HTTP_204_NO_CONTENT)
def join_club(club_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    student = _get_student_or_403(db, current_user)
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found.")
    existing = db.query(ClubMembership).filter(ClubMembership.student_id == student.id, ClubMembership.club_id == club_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already a member of this club.")
    db.add(ClubMembership(student_id=student.id, club_id=club_id, joined_at=datetime.now(timezone.utc)))
    db.commit()
