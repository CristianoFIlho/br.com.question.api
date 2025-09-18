from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Salesforce Quiz API"
    PROJECT_VERSION: str = "1.0.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://localhost:3000",
        "https://localhost:3001"
    ]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, list):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"


settings = Settings()
