"""
Pydantic Schemas
Request/Response models for API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., description="User message")
    session_id: str = Field(..., description="Session identifier")
    patient_name: Optional[str] = Field(None, description="Patient name if known")

class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str = Field(..., description="Agent response")
    agent: str = Field(..., description="Agent that handled the request")
    patient_data: Optional[Dict[str, Any]] = Field(None, description="Patient discharge data")
    sources: Optional[List[str]] = Field(None, description="Information sources")

class SystemStatus(BaseModel):
    """System status schema"""
    status: str
    patient_count: int
    vector_db_documents: int
    active_sessions: int

class PatientInfo(BaseModel):
    """Patient information schema"""
    patient_name: str
    discharge_date: str
    primary_diagnosis: str
    medications: List[str]
    dietary_restrictions: str
    follow_up: str
    warning_signs: str
    discharge_instructions: str
