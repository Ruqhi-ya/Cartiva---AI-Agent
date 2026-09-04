"""Application configuration loaded from environment variables.

Secrets (DB URL, LLM key, Razorpay keys, JWT secret) are never
hard-coded and never exposed to the frontend.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:postgres@localhost:5432/cartiva"
    )

    # LLM
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""
    LLM_PROVIDER: str = "mock"

    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # JWT authentication
    CARTIVA_JWT_SECRET: str = ""

    # Authentication cookie
    COOKIE_SECURE: bool = False

    # Usage limits
    FREE_MONTHLY_AI_SESSIONS: int = 10

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()