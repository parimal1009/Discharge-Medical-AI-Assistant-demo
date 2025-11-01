"""
FastAPI Main Application
Multi-Agent Post Discharge Medical AI Assistant
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import Dict, Any
import uvicorn

from backend.models.schemas import ChatRequest, ChatResponse, SystemStatus
from backend.database.patient_db import PatientDatabase
from backend.database.vector_db import VectorDatabase
from backend.agents.orchestrator import AgentOrchestrator
from backend.config import settings
from backend.utils.logger import system_logger, logger

# Initialize FastAPI app
app = FastAPI(
    title="Post Discharge Medical AI Assistant",
    description="Multi-agent system for post-discharge patient care",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
patient_db = PatientDatabase()
vector_db = VectorDatabase()
orchestrator = AgentOrchestrator(patient_db, vector_db)

# Session storage
active_sessions: Dict[str, Dict[str, Any]] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Post Discharge Medical AI Assistant...")
    
    # Initialize vector database from PDF
    if vector_db.get_collection_stats()["document_count"] == 0:
        logger.info("Initializing vector database from PDF...")
        vector_db.initialize_from_pdf()
    
    logger.info(f"System ready with {patient_db.get_patient_count()} patients and "
                f"{vector_db.get_collection_stats()['document_count']} knowledge documents")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint - routes messages through agent orchestrator
    """
    try:
        system_logger.log_system_event(
            "chat_request",
            {
                "session_id": request.session_id,
                "patient_name": request.patient_name or "Unknown",
                "message_length": len(request.message)
            }
        )
        
        # Initialize session if needed
        if request.session_id not in active_sessions:
            active_sessions[request.session_id] = {
                "patient_name": request.patient_name,
                "current_agent": "receptionist",
                "patient_data": None,
                "conversation_history": []
            }
        
        session = active_sessions[request.session_id]
        
        # Process through orchestrator
        response = await orchestrator.process_message(
            message=request.message,
            patient_name=request.patient_name or session.get("patient_name"),
            session=session
        )
        
        # Update session
        if response.get("patient_data"):
            session["patient_data"] = response["patient_data"]
            session["patient_name"] = response["patient_data"]["patient_name"]
        
        # Track current agent
        current_agent = response.get("agent", session.get("current_agent", "receptionist"))
        session["current_agent"] = current_agent
        session["session_id"] = request.session_id
        
        # Store conversation
        session["conversation_history"].append({
            "user": request.message,
            "assistant": response["response"],
            "agent": response.get("agent", "unknown")
        })
        
        return ChatResponse(
            response=response["response"],
            agent=response.get("agent", "receptionist"),
            patient_data=response.get("patient_data"),
            sources=response.get("sources")
        )
        
    except Exception as e:
        system_logger.log_error("chat_endpoint", str(e))
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/api/patient/{patient_name}")
async def get_patient_endpoint(patient_name: str):
    """
    Get patient information by name
    """
    try:
        patient_data = patient_db.get_patient(patient_name)
        
        if not patient_data:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return JSONResponse(content=patient_data)
        
    except HTTPException:
        raise
    except Exception as e:
        system_logger.log_error("get_patient_endpoint", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status", response_model=SystemStatus)
async def status_endpoint():
    """
    Get system status
    """
    try:
        vector_stats = vector_db.get_collection_stats()
        
        return SystemStatus(
            status="operational",
            patient_count=patient_db.get_patient_count(),
            vector_db_documents=vector_stats["document_count"],
            active_sessions=len(active_sessions)
        )
        
    except Exception as e:
        system_logger.log_error("status_endpoint", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def logs_endpoint():
    """
    Get recent system logs
    """
    try:
        log_file = Path(settings.LOG_FILE_PATH)
        
        if not log_file.exists():
            return JSONResponse(content={"logs": []})
        
        # Read last 100 lines
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_logs = lines[-100:]
        
        return JSONResponse(content={"logs": recent_logs})
        
    except Exception as e:
        system_logger.log_error("logs_endpoint", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the main HTML page"""
    html_path = Path("frontend/templates/index.html")
    if html_path.exists():
        return FileResponse(html_path)
    else:
        return JSONResponse(
            content={"message": "Frontend not found. API is operational."},
            status_code=200
        )

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
