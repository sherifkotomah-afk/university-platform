"""
FastAPI application entrypoint.
Deployed on Render — Render sets the PORT env var, so start command is:
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.routers import auth, academics, applications, fees, students, faculty, admin, content, inbox, campus, setup, uploads

settings = get_settings()

app = FastAPI(
    title="University Platform API",
    description="Backend API for the university web platform (public site, applicant portal, student portal, faculty portal, admin back office).",
    version="0.1.0",
)

allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(academics.router)
app.include_router(applications.router)
app.include_router(fees.router)
app.include_router(students.router)
app.include_router(faculty.router)
app.include_router(admin.router)
app.include_router(content.router)
app.include_router(inbox.router)
app.include_router(campus.router)
app.include_router(setup.router)
app.include_router(uploads.router)

# Serve uploaded files. See app/routers/uploads.py for the important note
# about Render's disk not being persistent across deploys.
os.makedirs(os.path.join(os.getcwd(), "uploads"), exist_ok=True)
app.mount("/uploads/static", StaticFiles(directory=os.path.join(os.getcwd(), "uploads")), name="uploads")


@app.get("/health", tags=["health"])
def health_check():
    """Render pings this to confirm the service is alive."""
    return {"status": "ok", "environment": settings.ENVIRONMENT}


@app.get("/", tags=["health"])
def root():
    return {"message": "University Platform API is running. See /docs for API documentation."}
