from pydantic_settings import BaseSettings
from typing import Dict, Any, List
import json
import os


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    face_recognition_tolerance: float = 0.4  # Stricter tolerance for better security
    gps_tolerance_meters: int = 100
    allowed_locations: Dict[str, Any] = {}
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        if not self.secret_key:
            raise ValueError("SECRET_KEY environment variable is required")
        
        # Parse allowed locations if provided as string
        locations_str = os.getenv("ALLOWED_LOCATIONS")
        if locations_str:
            try:
                self.allowed_locations = json.loads(locations_str)
            except json.JSONDecodeError:
                self.allowed_locations = {}
        
        # Parse CORS origins if provided as string
        cors_origins_str = os.getenv("CORS_ORIGINS")
        if cors_origins_str:
            try:
                self.cors_origins = json.loads(cors_origins_str)
            except json.JSONDecodeError:
                # Fallback to comma-separated string
                self.cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]


settings = Settings()