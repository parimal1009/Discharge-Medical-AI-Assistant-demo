"""
Web Search Tool for Current Medical Information
"""

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from backend.utils.logger import system_logger
from backend.config import settings

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False

class WebSearchInput(BaseModel):
    """Input schema for web search"""
    query: str = Field(description="Search query for medical information")

class WebSearchTool(BaseTool):
    """Tool for searching current medical information"""
    
    name: str = "web_search"
    description: str = (
        "Search the web for current medical information, recent research, "
        "and clinical guidelines. Use this when the question requires "
        "up-to-date information not in the knowledge base."
    )
    args_schema: Type[BaseModel] = WebSearchInput
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self):
        super().__init__()
        # Check if Tavily is available and configured
        tavily_available = TAVILY_AVAILABLE and settings.TAVILY_API_KEY
        if tavily_available:
            object.__setattr__(self, 'client', TavilyClient(api_key=settings.TAVILY_API_KEY))
            object.__setattr__(self, 'tavily_available', True)
        else:
            object.__setattr__(self, 'tavily_available', False)
    
    def _run(self, query: str) -> str:
        """Execute web search"""
        try:
            if not self.tavily_available:
                return self._fallback_response()
            
            # Enhanced query for medical content
            enhanced_query = f"medical nephrology {query} guidelines research"
            
            response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",
                max_results=3
            )
            
            if response.get('results'):
                results_text = "WEB SEARCH RESULTS (Current Medical Information):\n\n"
                for i, result in enumerate(response['results'][:3], 1):
                    results_text += f"{i}. {result['title']}\n"
                    results_text += f"   URL: {result['url']}\n"
                    results_text += f"   Summary: {result['content'][:250]}...\n\n"
                
                system_logger.log_web_search(query, len(response['results']), True)
                return results_text
            else:
                system_logger.log_web_search(query, 0, False)
                return "No recent web results found. Please consult medical professionals for current guidelines."
                
        except Exception as e:
            system_logger.log_error("web_search_tool", str(e))
            system_logger.log_web_search(query, 0, False)
            return self._fallback_response()
    
    async def _arun(self, query: str) -> str:
        """Async execution"""
        return self._run(query)
    
    def _fallback_response(self) -> str:
        """Fallback when web search unavailable"""
        return (
            "Web search is currently unavailable. "
            "Please consult your healthcare provider for the most current medical information."
        )
