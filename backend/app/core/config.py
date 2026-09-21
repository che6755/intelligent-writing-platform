# backend/app/core/config.py
import os
import sys
from pydantic_settings import BaseSettings

if getattr(sys, "frozen", False):
    DATA_DIR = os.path.dirname(sys.executable)
else:
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(DATA_DIR, 'writing_assistant.db')}"

    # LLM Configuration
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""

    class Config:
        env_file = os.path.join(DATA_DIR, ".env")
        env_file_encoding = 'utf-8'

settings = Settings()
