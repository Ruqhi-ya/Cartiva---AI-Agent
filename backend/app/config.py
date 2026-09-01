"""Application configuration loaded from environment variables.

Secrets (DB URL, LLM key, Razorpay keys) are never hard-coded and never
exposed to the frontend. The free usage limit is configurable here so it can
be changed without touching application logic.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database (uses psycopg v3 dialect)
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/cartiva"

    # LLM (integrated later)
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""
    LLM_PROVIDER: str = "mock"

    # Razorpay (integrated later)
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # Usage limits — configurable, not hard-coded across the app
    FREE_MONTHLY_AI_SESSIONS: int = 10

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
