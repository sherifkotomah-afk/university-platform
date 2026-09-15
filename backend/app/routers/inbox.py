from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from app.database import get_db
from app.models.core import User
from app.models.misc import Notification, Message, SupportTicket
from app.schemas.campus import (
    NotificationOut, SendMessageRequest, MessageOut, CreateSupportTicketRequest, SupportTicketOut
)
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/notifications", response_model=List[NotificationOut])
def my_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()


@router.patch("/notifications/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Notification not found.")
    note.read = True
    db.commit()


@router.post("/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(payload: SendMessageRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipient = db.query(User).filter(User.id == payload.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found.")
    message = Message(
        sender_id=current_user.id,
        recipient_id=payload.recipient_id,
        subject=payload.subject,
        body=payload.body,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/messages", response_model=List[MessageOut])
def my_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Message).filter(
        or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id)
    ).order_by(Message.sent_at.desc()).all()


@router.post("/support-tickets", response_model=SupportTicketOut, status_code=status.HTTP_201_CREATED)
def create_support_ticket(payload: CreateSupportTicketRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ticket = SupportTicket(
        user_id=current_user.id,
        category=payload.category,
        subject=payload.subject,
        description=payload.description,
        status="Open",
        created_at=datetime.now(timezone.utc),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/support-tickets/mine", response_model=List[SupportTicketOut])
def my_support_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SupportTicket).filter(SupportTicket.user_id == current_user.id).order_by(SupportTicket.created_at.desc()).all()


@router.get("/support-tickets", response_model=List[SupportTicketOut], dependencies=[Depends(require_role("admin", "registrar", "finance"))])
def all_support_tickets(status_filter: str = None, db: Session = Depends(get_db)):
    query = db.query(SupportTicket)
    if status_filter:
        query = query.filter(SupportTicket.status == status_filter)
    return query.order_by(SupportTicket.created_at.desc()).all()


@router.patch("/support-tickets/{ticket_id}/resolve", dependencies=[Depends(require_role("admin", "registrar", "finance"))])
def resolve_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    ticket.status = "Resolved"
    ticket.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return {"detail": "Ticket marked resolved."}
