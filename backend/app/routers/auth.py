"""
Auth endpoints.

Design decision: the public /auth/register endpoint ONLY ever creates
'applicant' accounts. Students, faculty, admins, registrars and finance
staff are created internally (by the admin back office, after acceptance
for students, or on hiring for staff) — never through public sign-up.
This mirrors how real universities control who gets institutional access.
"""
import hashlib
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models.core import User, UserSession
from app.schemas.auth import (
    RegisterApplicantRequest, LoginRequest, TokenResponse, RefreshRequest,
    ChangePasswordRequest, UserOut
)
from app.core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_token(token: str) -> str:
    # We never store raw refresh tokens, only their hash — same principle as passwords.
    return hashlib.sha256(token.encode()).hexdigest()


def _issue_tokens(db: Session, user: User) -> TokenResponse:
    access_token = create_access_token(subject=str(user.id), role=user.role)
    refresh_token = create_refresh_token(subject=str(user.id))

    from app.config import get_settings
    settings = get_settings()
    session = UserSession(
        user_id=user.id,
        refresh_token_hash=_hash_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
    )
    db.add(session)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token, role=user.role)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_applicant(payload: RegisterApplicantRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role="applicant",
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        must_change_password=False,  # they set their own password at signup
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="This account has been deactivated.")

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    return _issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")

    token_hash = _hash_token(payload.refresh_token)
    session = db.query(UserSession).filter(UserSession.refresh_token_hash == token_hash).first()
    if not session or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token not recognized or expired.")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User account not available.")

    # rotate: invalidate old session, issue new pair
    db.delete(session)
    db.commit()
    return _issue_tokens(db, user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    current_user.password_hash = hash_password(payload.new_password)
    current_user.must_change_password = False
    db.commit()


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
