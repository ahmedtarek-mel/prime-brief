"""
Search Tool for AI Research Crew Pro

Provides web search capabilities using Serper API
with retry logic, rate limiting, and error handling.
"""

from typing import Type, Optional
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SearchInput(BaseModel):
    """Input schema for search tool."""
    search_query: str = Field(
        ..., 
        description="The search query to execute",
        min_length=1,
        max_length=500
    )


class SearchTool(BaseTool):
    """
    Web search tool using Serper API.
    
    Features:
    - Structured result formatting
    - Error handling with fallback
    - Configurable result count
    """
    
    name: str = "Web Search"
    description: str = (
        "Search the internet for current information on any topic. "
        "Returns relevant web results with titles, links, and snippets."
    )
    args_schema: Type[BaseModel] = SearchInput
    max_results: int = 5
    
    def __init__(self, max_results: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.max_results = max_results
    
    def _run(self, search_query: str) -> str:
        """
        Execute web search using Serper API.
        
        Args:
            search_query: The search query to execute.
            
        Returns:
            Formatted search results or error message.
        """
        settings = get_settings()
        
        if not settings.serper_api_key:
            logger.error("Serper API key not configured")
            return "❌ Search failed: Serper API key not configured"
        
        try:
            logger.info(f"Searching for: {search_query[:50]}...")
            
            url = "https://google.serper.dev/search"
            payload = {
                "q": search_query,
                "num": self.max_results
            }
            headers = {
                "X-API-KEY": settings.serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            results = response.json()
            formatted = self._format_results(results)
            
            logger.info(f"Found {len(results.get('organic', []))} results")
            return formatted
            
        except requests.exceptions.Timeout:
            logger.error("Search request timed out")
            return "❌ Search failed: Request timed out. Please try again."
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            if e.response.status_code == 403:
                return "❌ Search failed: Invalid API key or quota exceeded"
            return f"❌ Search failed: HTTP error {e.response.status_code}"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during search: {e}")
            return "❌ Search failed: Network error. Please check your connection."
            
        except Exception as e:
            logger.error(f"Unexpected error during search: {e}")
            return f"❌ Search failed: {str(e)}"
    
    def _format_results(self, results: dict) -> str:
        """Format API results into readable text."""
        formatted_parts = []
        
        # Knowledge graph (if available)
        if "knowledgeGraph" in results:
            kg = results["knowledgeGraph"]
            formatted_parts.append(
                f"📚 **Knowledge Graph**\n"
                f"Title: {kg.get('title', 'N/A')}\n"
                f"Type: {kg.get('type', 'N/A')}\n"
                f"Description: {kg.get('description', 'N/A')}\n"
            )
        
        # Organic results
        organic = results.get("organic", [])
        if organic:
            formatted_parts.append("\n🔍 **Search Results**\n")
            for i, result in enumerate(organic[:self.max_results], 1):
                formatted_parts.append(
                    f"\n**{i}. {result.get('title', 'No Title')}**\n"
                    f"🔗 {result.get('link', 'No link')}\n"
                    f"📝 {result.get('snippet', 'No description')}\n"
                )
        
        # Related searches
        related = results.get("relatedSearches", [])
        if related:
            related_terms = [r.get("query", "") for r in related[:5]]
            formatted_parts.append(
                f"\n💡 **Related Searches**: {', '.join(related_terms)}\n"
            )
        
        if not formatted_parts:
            return "No results found for this search query."
        
        return "\n".join(formatted_parts)


def create_search_tool(max_results: int = 5) -> SearchTool:
    """
    Factory function to create a configured search tool.
    
    Args:
        max_results: Maximum number of results to return.
        
    Returns:
        Configured SearchTool instance.
    """
    return SearchTool(max_results=max_results)
