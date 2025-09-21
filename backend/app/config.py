import os
from pydantic import BaseModel


class Settings(BaseModel):
    APP_URL: str = os.getenv("APP_URL", "http://localhost:5173")
    ENV: str = os.getenv("ENV", "development")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "devsecret")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/studybuddy")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    S3_ACCESS_KEY_ID: str = os.getenv("S3_ACCESS_KEY_ID", "minioadmin")
    S3_SECRET_ACCESS_KEY: str = os.getenv("S3_SECRET_ACCESS_KEY", "minioadmin")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "studybuddy")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_OCR_MODEL: str = os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-latest")
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral")
    OLLAMA_OCR_MODEL: str = os.getenv("OLLAMA_OCR_MODEL", "mistral-ocr-2503")
    OCR_ENGINE: str = os.getenv("OCR_ENGINE", "tesseract")  # tesseract|ollama
    OCR_MAX_PAGES: int = int(os.getenv("OCR_MAX_PAGES", "20"))


settings = Settings()
