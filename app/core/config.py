"""
LankaAgent Core Configuration
"""
from functools import lru_cache

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "LankaAgent API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_KEY_HEADER: str = "X-API-Key"

    # Database
    DATABASE_URL: PostgresDsn = "postgresql://lankaagent:changeme@localhost:5432/lankaagent"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # Redis
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DECODE_RESPONSES: bool = True

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_BURST: int = 20

    # Tenant Resolution
    TENANT_HEADER: str = "X-Tenant-ID"
    TENANT_SUBDOMAIN_ENABLED: bool = True

    # WhatsApp (Twilio)
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_WHATSAPP_NUMBER: str | None = None
    TWILIO_WEBHOOK_URL: str | None = None

    # Meta WhatsApp Business API (Production)
    META_VERIFY_TOKEN: str | None = None
    META_APP_SECRET: str | None = None
    META_ACCESS_TOKEN: str | None = None
    META_PHONE_NUMBER_ID: str | None = None
    META_WABA_ID: str | None = None

    # Payments - Stripe
    STRIPE_SECRET_KEY: str | None = None
    STRIPE_PUBLISHABLE_KEY: str | None = None
    STRIPE_WEBHOOK_SECRET: str | None = None
    STRIPE_API_VERSION: str = "2024-04-10"

    # Payments - PayHere (Sri Lanka)
    PAYHERE_MERCHANT_ID: str | None = None
    PAYHERE_MERCHANT_SECRET: str | None = None
    PAYHERE_SANDBOX: bool = True
    PAYHERE_WEBHOOK_URL: str | None = None

    # MCP Server
    MCP_SERVER_URL: str = "http://localhost:8001"
    MCP_API_KEY: str | None = None

    # Google Calendar
    GOOGLE_CALENDAR_CLIENT_ID: str | None = None
    GOOGLE_CALENDAR_CLIENT_SECRET: str | None = None
    GOOGLE_CALENDAR_REDIRECT_URI: str | None = None

    # Google Maps
    GOOGLE_MAPS_API_KEY: str | None = None

    # Observability
    POSTHOG_API_KEY: str | None = None
    POSTHOG_HOST: str = "https://app.posthog.com"
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str | None = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # LLM Providers
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "deepseek/deepseek-chat-v3-0324"
    ZEN_API_KEY: str | None = None
    ZEN_BASE_URL: str = "https://opencode.ai/zen/v1"
    ZEN_MODEL: str = "deepseek-v4-flash-free"
    LLM_MODEL_PRIMARY: str = "nvidia/nemotron-3-ultra"
    LLM_MODEL_FALLBACK_1: str = "anthropic/claude-3.5-sonnet"
    LLM_MODEL_FALLBACK_2: str = "openai/gpt-4o"
    LLM_TEMPERATURE_EXTRACTION: float = 0.1
    LLM_TEMPERATURE_GENERATION: float = 0.7
    LLM_MAX_TOKENS: int = 4096

    # Email (Postmark)
    POSTMARK_SERVER_TOKEN: str | None = None
    POSTMARK_FROM_EMAIL: str = "noreply@lankaagent.com"
    POSTMARK_FROM_NAME: str = "LankaAgent"

    # Feature Flags
    ENABLE_WELLNESS_ENGINE: bool = True
    ENABLE_MULTILINGUAL: bool = True
    ENABLE_ANALYTICS: bool = True
    ENABLE_WEBHOOK_RETRY: bool = True
    MOCK_EXTERNAL_APIS: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json, console

    # File Uploads
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_FILE_TYPES: list[str] = ["image/jpeg", "image/png", "application/pdf"]

    # Backup
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_S3_BUCKET: str | None = None
    BACKUP_S3_REGION: str = "eu-central-1"

    # Compliance
    DATA_RETENTION_DAYS: int = 730  # 2 years
    GDPR_COMPLIANCE: bool = True
    PDPA_COMPLIANCE: bool = True

    # Wellness/Ayurveda
    BIMARI_API_URL: str | None = None
    BIMARI_API_KEY: str | None = None
    WELLNESS_COMMISSION_RATE: float = 0.15  # 15%

    # SLTDA
    SLTDA_API_URL: str | None = None
    SLTDA_API_KEY: str | None = None

    NGROK_URL: str | None = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
