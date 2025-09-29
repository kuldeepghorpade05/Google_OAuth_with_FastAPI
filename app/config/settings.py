from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "OAuth FastAPI App"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Security
    SESSION_SECRET: str
    SESSION_MAX_AGE: int = 86400
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    OAUTH_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/auth/callback"
    
    # CORS - Handle as string and convert to list
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Convert comma-separated string to list of origins"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()