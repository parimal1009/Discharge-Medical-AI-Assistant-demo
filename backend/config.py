"""
Configuration Management
Centralized settings for the application
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    GROQ_API_KEY: str = ""
    TAVILY_API_KEY: Optional[str] = None
    
    # Model Configuration
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    EMBEDDINGS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database Paths
    PATIENT_DB_PATH: str = "./data/patient_reports.json"
    VECTOR_DB_PATH: str = "./data/vector_store"
    PDF_PATH: str = "./data/comprehensive-clinical-nephrology.pdf"
    
    # Vector Store Configuration
    CHROMA_COLLECTION_NAME: str = "nephrology_knowledge"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 3
    
    # Logging
    LOG_FILE_PATH: str = "./logs/system.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()

def create_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "logs",
        "backend/agents",
        "backend/database",
        "backend/models",
        "backend/tools",
        "backend/utils",
        "frontend/templates",
        "frontend/static/css",
        "frontend/static/js"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
