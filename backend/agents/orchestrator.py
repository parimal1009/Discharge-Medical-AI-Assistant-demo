"""
Agent Orchestrator - Improved Version
Manages multi-agent workflow with better prompt engineering and error handling
"""

from typing import Dict, Any, Optional
from backend.database.patient_db import PatientDatabase
from backend.database.vector_db import VectorDatabase
from backend.tools.patient_retrieval import PatientRetrievalTool
from backend.tools.web_search_tool import WebSearchTool
from backend.utils.logger import system_logger
from backend.config import settings

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub

class AgentOrchestrator:
    """Orchestrates multi-agent system"""
    
    def __init__(self, patient_db: PatientDatabase, vector_db: VectorDatabase):
        self.patient_db = patient_db
        self.vector_db = vector_db
        
        # Initialize LLM with better settings
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=0.3  # Slightly higher for more natural responses
        )
        
        # Initialize tools
        self.patient_tool = PatientRetrievalTool(patient_db)
        self.web_search_tool = WebSearchTool()
        
        # Load prompt template
        self.prompt = hub.pull("hwchase17/react")
        
        system_logger.log_system_event("orchestrator_initialized", {})
    
    async def process_message(
        self,
        message: str,
        patient_name: Optional[str],
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message through appropriate agent"""
        
        # Check if message requires clinical agent
        if self._is_clinical_query(message):
            session["current_agent"] = "clinical"
            return await self._process_clinical(message, session)
        
        # Otherwise use receptionist
        session["current_agent"] = "receptionist"
        return await self._process_receptionist(message, patient_name, session)
    
    async def _process_receptionist(
        self,
        message: str,
        patient_name: Optional[str],
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process through receptionist agent"""
        
        try:
            # Check if we already have patient data in session
            if session.get("patient_data"):
                # Skip agent call, respond directly with cached data
                return self._create_direct_response(message, session)
            
            # Try to extract patient name if not provided
            if not patient_name:
                patient_name = self._extract_patient_name(message)
            
            # If we have a name, try direct lookup first
            if patient_name:
                patient_data = self.patient_db.get_patient(patient_name)
                if patient_data:
                    session["patient_data"] = patient_data
                    session["patient_name"] = patient_name
                    return self._create_welcome_response(patient_data)
            
            # Create receptionist agent only if needed
            receptionist = create_react_agent(
                llm=self.llm,
                tools=[self.patient_tool],
                prompt=self.prompt
            )
            
            executor = AgentExecutor(
                agent=receptionist,
                tools=[self.patient_tool],
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,  # Increased from 3
                max_execution_time=30,  # Reduced from 60
                early_stopping_method="generate"  # Better stopping
            )
            
            # Simplified, more direct prompt
            user_input = f"""You are a medical receptionist. The patient said: "{message}"

Task: Use the patient_retrieval tool to find their discharge information, then greet them warmly with a brief summary.

Important: Call the tool once and use the results immediately. Be concise."""

            result = await executor.ainvoke({"input": user_input})
            
            # Extract response
            agent_output = result.get("output", "")
            
            # Check if clinical agent needed
            requires_clinical = self._check_clinical_needed(message, agent_output)
            
            response = {
                "response": agent_output,
                "agent": "receptionist",
                "requires_clinical": requires_clinical
            }
            
            # Try to extract patient data from agent's tool usage
            if patient_name and not session.get("patient_data"):
                patient_data = self.patient_db.get_patient(patient_name)
                if patient_data:
                    response["patient_data"] = patient_data
                    session["patient_data"] = patient_data
                    session["patient_name"] = patient_name
            
            system_logger.log_agent_interaction(
                "receptionist",
                patient_name or "unknown",
                message,
                agent_output,
                session.get("session_id", "unknown")
            )
            
            if requires_clinical:
                system_logger.log_agent_handoff(
                    "receptionist",
                    "clinical",
                    patient_name or "unknown",
                    "Medical query detected",
                    session.get("session_id", "unknown")
                )
            
            return response
            
        except Exception as e:
            system_logger.log_error("receptionist_agent", str(e))
            
            # Fallback: try direct database lookup
            if patient_name:
                patient_data = self.patient_db.get_patient(patient_name)
                if patient_data:
                    session["patient_data"] = patient_data
                    return self._create_welcome_response(patient_data)
            
            return {
                "response": "Hello! I'd be happy to help you. Could you please provide your full name so I can look up your information?",
                "agent": "receptionist",
                "requires_clinical": False
            }
    
    def _create_direct_response(
        self,
        message: str,
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create response when patient data is already loaded"""
        
        patient_data = session.get("patient_data", {})
        patient_name = session.get("patient_name", "")
        
        # Simple greeting response
        response_text = f"""Hello {patient_name}! I have your discharge information here. 
        
You were diagnosed with {patient_data.get('primary_diagnosis', 'N/A')} and discharged on {patient_data.get('discharge_date', 'N/A')}.

How are you feeling today?"""
        
        return {
            "response": response_text,
            "agent": "receptionist",
            "requires_clinical": self._is_clinical_query(message),
            "patient_data": patient_data
        }
    
    def _create_welcome_response(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create welcome response with patient data"""
        
        response_text = f"""Hello {patient_data.get('name')}! Welcome back.

I have your discharge information from {patient_data.get('discharge_date', 'recently')}. You were treated for {patient_data.get('primary_diagnosis', 'your condition')}.

How can I help you today?"""
        
        return {
            "response": response_text,
            "agent": "receptionist",
            "requires_clinical": False,
            "patient_data": patient_data
        }
    
    def _extract_patient_name(self, message: str) -> Optional[str]:
        """Try to extract patient name from message"""
        # Simple heuristic: if message is 2-3 words and looks like a name
        words = message.strip().split()
        if len(words) == 2 and all(w[0].isupper() for w in words):
            return message.strip()
        return None
    
    async def _process_clinical(
        self,
        message: str,
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process through clinical agent with RAG"""
        
        try:
            # Get relevant knowledge from vector DB
            rag_results = self.vector_db.search(message, n_results=3)
            rag_context = self._format_rag_context(rag_results)
            
            # Create clinical agent with web search
            clinical = create_react_agent(
                llm=ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model_name=settings.GROQ_MODEL,
                    temperature=0.1  # Lower for medical accuracy
                ),
                tools=[self.web_search_tool],
                prompt=self.prompt
            )
            
            executor = AgentExecutor(
                agent=clinical,
                tools=[self.web_search_tool],
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,  # Increased
                max_execution_time=45,  # Reasonable timeout
                early_stopping_method="generate"
            )
            
            # Build clinical prompt - more concise
            patient_context = ""
            if session.get("patient_data"):
                pd = session["patient_data"]
                patient_context = f"""Patient Info: {pd.get('primary_diagnosis')} | Meds: {', '.join(pd.get('medications', [])[:3])}"""
            
            user_input = f"""Clinical question: "{message}"

{patient_context}

Knowledge base:
{rag_context}

Provide a clear, accurate answer. Use web_search only if needed for current guidelines. Include standard medical disclaimer."""

            result = await executor.ainvoke({"input": user_input})
            
            # Extract sources
            sources = [r['metadata'].get('source', 'Nephrology Knowledge Base') 
                      for r in rag_results[:2]]  # Limit sources
            
            agent_output = result.get("output", "")
            if "web search" in agent_output.lower() or "searched" in agent_output.lower():
                sources.append("Web Search Results")
            
            response = {
                "response": agent_output,
                "agent": "clinical",
                "sources": list(set(sources)),
                "patient_data": session.get("patient_data")
            }
            
            system_logger.log_agent_interaction(
                "clinical",
                session.get("patient_name", "unknown"),
                message,
                agent_output,
                session.get("session_id", "unknown")
            )
            
            return response
            
        except Exception as e:
            system_logger.log_error("clinical_agent", str(e))
            return {
                "response": "I apologize, but I'm having difficulty answering that. Please consult your healthcare provider for personalized medical advice.",
                "agent": "clinical",
                "sources": []
            }
    
    def _is_clinical_query(self, message: str) -> bool:
        """Determine if message is a clinical/medical question"""
        clinical_keywords = [
            'symptom', 'pain', 'swelling', 'medication', 'side effect',
            'blood', 'urine', 'pressure', 'kidney', 'dialysis', 'transplant',
            'doctor', 'treatment', 'diagnosis', 'test', 'lab', 'medical',
            'diet', 'food', 'eat', 'drink', 'exercise', 'restriction',
            'how should', 'what should', 'can i', 'is it safe', 'advice',
            'health', 'care', 'manage', 'control', 'prevent', 'creatinine',
            'egfr', 'albumin', 'potassium', 'sodium', 'phosphorus'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in clinical_keywords)
    
    def _check_clinical_needed(self, message: str, response: str) -> bool:
        """Determine if clinical agent is needed"""
        return self._is_clinical_query(message)
    
    def _format_rag_context(self, rag_results: list) -> str:
        """Format RAG results for context"""
        if not rag_results:
            return "No specific medical information found in knowledge base."
        
        context_parts = []
        for i, result in enumerate(rag_results[:3], 1):  # Limit to top 3
            content = result.get('content', '')[:400]  # Truncate for brevity
            context_parts.append(f"{i}. {content}...")
        
        return "\n".join(context_parts)
