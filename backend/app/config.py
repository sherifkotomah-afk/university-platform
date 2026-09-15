"""
Central application configuration.
All values are loaded from environment variables so nothing sensitive
is hardcoded. On Render, set these under the service's Environment tab.
On Supabase, DATABASE_URL comes from Project Settings -> Database -> Connection string (URI, "Session pooler" recommended for Render).
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # --- Database (Supabase Postgres connection string) ---
    DATABASE_URL: str

    # --- Auth / JWT ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS (your Vercel frontend URL(s), comma-separated) ---
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # --- Paystack ---
    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""

    # --- Institution defaults (can be overridden via institution_settings table) ---
    DEFAULT_INSTITUTION_NAME: str = "Sample University"

    # --- Environment ---
    ENVIRONMENT: str = "development"  # "development" | "production"

    # --- One-time setup ---
    # Used only by /setup/bootstrap to create the first admin account +
    # institution settings, so this never has to be done via a terminal
    # or a seed script — just a single browser request via /docs.
    SETUP_SECRET_KEY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
