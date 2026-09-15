"""
One-time setup endpoint.

This exists so the very first admin account and institution settings can be
created entirely through the browser (via the auto-generated Swagger UI at
/docs) — no terminal, no seed script, no local database access needed.

Protected by SETUP_SECRET_KEY (an env var only you know) and by refusing to
run a second time once an admin already exists, so it can't be abused after
initial setup.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.database import get_db
from app.config import get_settings
from app.models.core import User, InstitutionSettings
from app.core.security import hash_password

router = APIRouter(prefix="/setup", tags=["setup"])
settings = get_settings()


class BootstrapRequest(BaseModel):
    setup_secret: str
    institution_name: str
    short_code: str
    grading_system: str = "GPA"  # 'GPA' or 'CWA'
    academic_year: str
    admin_email: EmailStr
    admin_password: str
    admin_first_name: str
    admin_last_name: str


@router.post("/bootstrap", status_code=status.HTTP_201_CREATED)
def bootstrap(payload: BootstrapRequest, db: Session = Depends(get_db)):
    if not settings.SETUP_SECRET_KEY or payload.setup_secret != settings.SETUP_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid setup secret.")

    existing_admin = db.query(User).filter(User.role == "admin").first()
    if existing_admin:
        raise HTTPException(
            status_code=400,
            detail="Setup has already been completed — an admin account already exists. "
                   "This endpoint only runs once, for security.",
        )

    existing_settings = db.query(InstitutionSettings).first()
    if not existing_settings:
        db.add(InstitutionSettings(
            institution_name=payload.institution_name,
            short_code=payload.short_code,
            grading_system=payload.grading_system,
            academic_year=payload.academic_year,
            current_semester=1,
        ))

    admin_user = User(
        email=payload.admin_email,
        password_hash=hash_password(payload.admin_password),
        role="admin",
        first_name=payload.admin_first_name,
        last_name=payload.admin_last_name,
        must_change_password=True,
    )
    db.add(admin_user)
    db.commit()

    return {
        "detail": "Setup complete. Institution settings created and first admin account created. "
                  "Log in at /auth/login with the admin email/password you just set — "
                  "you'll be required to change the password on first login.",
        "admin_email": payload.admin_email,
    }


@router.get("/status")
def setup_status(db: Session = Depends(get_db)):
    """Lets you check from the browser whether setup has already run."""
    admin_exists = db.query(User).filter(User.role == "admin").first() is not None
    settings_exist = db.query(InstitutionSettings).first() is not None
    return {"admin_account_exists": admin_exists, "institution_settings_exist": settings_exist}
