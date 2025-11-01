"""
Agent Orchestrator
Manages multi-agent workflow and routing between receptionist and clinical agents
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
        
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL
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
        
        current_agent = session.get("current_agent", "receptionist")
        
        if current_agent == "receptionist":
            return await self._process_receptionist(message, patient_name, session)
        else:
            return await self._process_clinical(message, session)
    
    async def _process_receptionist(
        self,
        message: str,
        patient_name: Optional[str],
        session: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process through receptionist agent"""
        
        try:
            # Create receptionist agent
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
                max_iterations=10,
                max_execution_time=60
            )
            
            # Build prompt - simpler format for ReAct agent
            user_input = f"""I am a friendly medical receptionist. A patient said: "{message}"

I should:
1. If they provided a name, use the patient_retrieval tool to get their discharge report
2. Greet them warmly and ask about their recovery
3. If they ask medical questions, note that I'll connect them with our clinical team

Let me help this patient now."""

            result = await executor.ainvoke({"input": user_input})
            
            # Check if clinical agent needed
            requires_clinical = self._check_clinical_needed(message, result["output"])
            
            response = {
                "response": result["output"],
                "agent": "receptionist",
                "requires_clinical": requires_clinical
            }
            
            # Try to extract patient data
            if patient_name and not session.get("patient_data"):
                patient_data = self.patient_db.get_patient(patient_name)
                if patient_data:
                    response["patient_data"] = patient_data
            
            system_logger.log_agent_interaction(
                "receptionist",
                patient_name or "unknown",
                message,
                result["output"],
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
            return {
                "response": "I apologize for the confusion. Could you please rephrase that?",
                "agent": "receptionist",
                "requires_clinical": False
            }
    
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
                max_iterations=10,
                max_execution_time=60
            )
            
            # Build clinical prompt
            patient_context = ""
            if session.get("patient_data"):
                pd = session["patient_data"]
                patient_context = f"""
PATIENT CONTEXT:
- Diagnosis: {pd.get('primary_diagnosis')}
- Medications: {', '.join(pd.get('medications', []))}
- Warning Signs: {pd.get('warning_signs')}
"""
            
            user_input = f"""I am a clinical AI assistant. Patient question: "{message}"

{patient_context}

Relevant knowledge from database:
{rag_context}

I must:
1. Answer using the knowledge base provided above
2. Use web_search tool only if current guidelines are needed
3. Include disclaimer: "This is for educational purposes. Consult healthcare professionals."
4. Cite sources

Let me provide a helpful, accurate response."""

            result = await executor.ainvoke({"input": user_input})
            
            # Extract sources
            sources = [r['metadata'].get('source', 'Nephrology Knowledge Base') for r in rag_results]
            if "web search" in result["output"].lower():
                sources.append("Web Search Results")
            
            response = {
                "response": result["output"],
                "agent": "clinical",
                "sources": list(set(sources)),
                "patient_data": session.get("patient_data")
            }
            
            system_logger.log_agent_interaction(
                "clinical",
                session.get("patient_name", "unknown"),
                message,
                result["output"],
                session.get("session_id", "unknown")
            )
            
            return response
            
        except Exception as e:
            system_logger.log_error("clinical_agent", str(e))
            return {
                "response": "I apologize, but I'm having difficulty answering that. Please consult your healthcare provider.",
                "agent": "clinical",
                "sources": []
            }
    
    def _check_clinical_needed(self, message: str, response: str) -> bool:
        """Determine if clinical agent is needed"""
        clinical_keywords = [
            'symptom', 'pain', 'swelling', 'medication', 'side effect',
            'blood', 'urine', 'pressure', 'kidney', 'dialysis', 'transplant',
            'doctor', 'treatment', 'diagnosis', 'test', 'lab', 'medical'
        ]
        
        combined = (message + " " + response).lower()
        return any(keyword in combined for keyword in clinical_keywords)
    
    def _format_rag_context(self, rag_results: list) -> str:
        """Format RAG results for context"""
        if not rag_results:
            return "No specific nephrology information found."
        
        context = "RELEVANT MEDICAL INFORMATION:\n\n"
        for i, result in enumerate(rag_results, 1):
            context += f"{i}. {result['content'][:500]}...\n\n"
        
        return context
