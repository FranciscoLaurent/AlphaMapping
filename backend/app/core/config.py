from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

# Get the backend directory path (go up 3 levels from backend/app/core/config.py)
BACKEND_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"

class Settings(BaseSettings):
    APP_NAME: str = "AlphaMapping"
    DEBUG: bool = True
    
    # API KEYS
    FOFA_EMAIL: str = ""
    FOFA_KEY: str = ""
    ZOOMEYE_KEY: str = ""
    
    # LLM SETTINGS
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    
    # DATABASE
    DATABASE_URL: str = "sqlite:///./data/alpha_mapping.db"
    
    # REPORTS
    REPORTS_DIR: str = "./data/reports"
    
    # GEOLOCATION
    IP_GEOLOCATION_API: str = "http://ip-api.com/json/"

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
