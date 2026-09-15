"""
Public content management — news, events, and staff directory.
Read endpoints are public (power the website). Write endpoints require admin.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.misc import NewsPost, Event, StaffDirectory
from app.models.faculty import FacultyProfile  # noqa
from app.models.academics import Department
from app.schemas.campus import (
    NewsPostOut, CreateNewsPostRequest, EventOut, CreateEventRequest, StaffDirectoryOut
)
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/content", tags=["content"])


@router.get("/news", response_model=List[NewsPostOut])
def list_news(db: Session = Depends(get_db)):
    return db.query(NewsPost).filter(NewsPost.published == True).order_by(NewsPost.published_at.desc()).all()  # noqa: E712


@router.get("/news/{post_id}", response_model=NewsPostOut)
def get_news_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(NewsPost).filter(NewsPost.id == post_id, NewsPost.published == True).first()  # noqa: E712
    if not post:
        raise HTTPException(status_code=404, detail="News post not found.")
    return post


@router.post("/news", response_model=NewsPostOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin"))])
def create_news_post(payload: CreateNewsPostRequest, db: Session = Depends(get_db),
                      current_user: User = Depends(require_role("admin"))):
    post = NewsPost(
        title=payload.title,
        body=payload.body,
        cover_image_url=payload.cover_image_url,
        published=payload.published,
        author_id=current_user.id,
        published_at=datetime.now(timezone.utc) if payload.published else None,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.get("/events", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db)):
    return db.query(Event).order_by(Event.start_time).all()


@router.post("/events", response_model=EventOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_role("admin"))])
def create_event(payload: CreateEventRequest, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/directory", response_model=List[StaffDirectoryOut])
def staff_directory(db: Session = Depends(get_db)):
    rows = db.query(StaffDirectory).all()
    result = []
    for row in rows:
        user = row.user_id and db.get(User, row.user_id)
        dept = row.department_id and db.get(Department, row.department_id)
        if not user:
            continue
        result.append(StaffDirectoryOut(
            id=row.id,
            title=row.title,
            office_location=row.office_location,
            public_email=row.public_email,
            photo_url=row.photo_url,
            first_name=user.first_name,
            last_name=user.last_name,
            department_name=dept.name if dept else None,
        ))
    return result
