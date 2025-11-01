"""
Setup and Run Script
Initializes the system and starts the server
"""

import sys
from pathlib import Path
import uvicorn

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.config import settings, create_directories
from backend.database.patient_db import PatientDatabase
from backend.database.vector_db import VectorDatabase
from backend.utils.logger import logger

def setup_system():
    """Initialize system components"""
    logger.info("=" * 60)
    logger.info("Post Discharge Medical AI Assistant - Setup")
    logger.info("=" * 60)
    
    # Create directories
    create_directories()
    logger.info("✓ Directories created")
    
    # Initialize patient database
    patient_db = PatientDatabase()
    logger.info(f"✓ Patient database loaded: {patient_db.get_patient_count()} patients")
    
    # Initialize vector database
    vector_db = VectorDatabase()
    stats = vector_db.get_collection_stats()
    
    if stats["document_count"] == 0:
        logger.info("Initializing vector database from PDF...")
        success = vector_db.initialize_from_pdf()
        if success:
            stats = vector_db.get_collection_stats()
            logger.info(f"✓ Vector database initialized: {stats['document_count']} documents")
        else:
            logger.warning("⚠ Vector database initialization failed, using fallback knowledge")
    else:
        logger.info(f"✓ Vector database loaded: {stats['document_count']} documents")
    
    logger.info("=" * 60)
    logger.info("System ready!")
    logger.info(f"Server will start at: http://{settings.HOST}:{settings.PORT}")
    logger.info("=" * 60)

if __name__ == "__main__":
    setup_system()
    
    # Start server
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
