from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterApplicantRequest(BaseModel):
    """Public sign-up is only ever for applicants — every other role
    (student, faculty, admin) is created internally by the admin panel,
    never through public self-registration."""
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    must_change_password: bool

    class Config:
        from_attributes = True
