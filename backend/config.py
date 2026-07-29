import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VeriPix API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-veripix-jwt-key-change-in-prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./veripix.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SERP_API_KEY: str = os.getenv("SERP_API_KEY", "")
    
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp", "image/heic"]
    ALLOWED_VIDEO_TYPES: list[str] = ["video/mp4", "video/quicktime", "video/webm"]

    class Config:
        case_sensitive = True

settings = Settings()
