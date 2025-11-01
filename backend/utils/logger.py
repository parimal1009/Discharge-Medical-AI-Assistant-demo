"""
Comprehensive Logging System
Tracks all system interactions, agent activities, and errors
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
from backend.config import settings

class SystemLogger:
    """Comprehensive system logger"""
    
    def __init__(self):
        self.log_file = settings.LOG_FILE_PATH
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure loguru logger"""
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            lambda msg: print(msg, end=""),
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
            level=settings.LOG_LEVEL
        )
        
        # Add file handler
        logger.add(
            self.log_file,
            rotation="10 MB",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level="DEBUG"
        )
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]):
        """Log system-level events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        logger.info(f"SYSTEM_EVENT: {json.dumps(log_entry)}")
    
    def log_agent_interaction(
        self,
        agent_name: str,
        patient_name: str,
        user_message: str,
        agent_response: str,
        session_id: str
    ):
        """Log agent interactions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "patient": patient_name,
            "session_id": session_id,
            "user_message": user_message[:200],
            "agent_response": agent_response[:200]
        }
        logger.info(f"AGENT_INTERACTION: {json.dumps(log_entry)}")
    
    def log_agent_handoff(
        self,
        from_agent: str,
        to_agent: str,
        patient_name: str,
        reason: str,
        session_id: str
    ):
        """Log agent handoffs"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "patient": patient_name,
            "reason": reason,
            "session_id": session_id
        }
        logger.warning(f"AGENT_HANDOFF: {json.dumps(log_entry)}")
    
    def log_patient_retrieval(
        self,
        patient_name: str,
        success: bool,
        details: str = ""
    ):
        """Log patient data retrieval"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "patient_name": patient_name,
            "success": success,
            "details": details
        }
        logger.info(f"PATIENT_RETRIEVAL: {json.dumps(log_entry)}")
    
    def log_rag_query(
        self,
        query: str,
        num_results: int,
        success: bool,
        sources: Optional[list] = None
    ):
        """Log RAG queries"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:200],
            "num_results": num_results,
            "success": success,
            "sources": sources or []
        }
        logger.info(f"RAG_QUERY: {json.dumps(log_entry)}")
    
    def log_web_search(
        self,
        query: str,
        num_results: int,
        success: bool
    ):
        """Log web search queries"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query[:200],
            "num_results": num_results,
            "success": success
        }
        logger.info(f"WEB_SEARCH: {json.dumps(log_entry)}")
    
    def log_tool_usage(
        self,
        tool_name: str,
        input_data: str,
        output_summary: str,
        success: bool
    ):
        """Log tool usage"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "input": input_data[:200],
            "output": output_summary[:200],
            "success": success
        }
        logger.info(f"TOOL_USAGE: {json.dumps(log_entry)}")
    
    def log_error(self, component: str, error_message: str):
        """Log errors"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error": error_message
        }
        logger.error(f"ERROR: {json.dumps(log_entry)}")

# Global logger instance
system_logger = SystemLogger()
