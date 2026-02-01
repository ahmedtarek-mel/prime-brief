"""
Web Researcher Agent for AI Research Crew Pro

Specialized agent for conducting comprehensive web research
using Serper API for search capabilities.
"""

from crewai import Agent

from .base_agent import AgentFactory, AgentConfig
from app.tools import create_search_tool
from app.utils.logger import get_logger

logger = get_logger(__name__)


RESEARCHER_BACKSTORY = """You are an elite web research specialist with over a decade 
of experience in investigative journalism and academic research. Your expertise lies in:

- Finding credible, authoritative sources across the internet
- Distinguishing reliable information from misinformation
- Synthesizing complex data from multiple sources
- Identifying emerging trends and expert opinions
- Fact-checking and source verification

You approach every research task methodically:
1. First, understand the core question and its context
2. Search for primary sources and expert opinions
3. Cross-reference information across multiple sources
4. Note publication dates and source credibility
5. Compile findings with proper citations

You are known for your thoroughness, accuracy, and ability to find 
information others might miss. You always prioritize quality over quantity."""


def create_researcher_agent(
    topic: str,
    num_results: int = 5
) -> Agent:
    """
    Create a configured Web Researcher agent.
    
    Args:
        topic: The research topic to focus on.
        num_results: Number of search results to retrieve.
        
    Returns:
        Configured Agent instance for web research.
    """
    logger.info(f"Creating researcher agent for topic: {topic[:50]}...")
    
    search_tool = create_search_tool(max_results=num_results)
    
    config = AgentConfig(
        role="Senior Web Research Specialist",
        goal=f"Conduct comprehensive, accurate web research on: {topic}",
        backstory=RESEARCHER_BACKSTORY,
        tools=[search_tool],
        max_iter=5,
        allow_delegation=False,
    )
    
    return AgentFactory.create_agent(config)
