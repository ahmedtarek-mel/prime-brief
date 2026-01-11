"""
Email Coordinator Agent for AI Research Crew Pro

Specialized agent for crafting and sending professional
email reports with research findings.
"""

from crewai import Agent

from .base_agent import AgentFactory, AgentConfig
from app.tools import create_email_tool
from app.utils.logger import get_logger

logger = get_logger(__name__)


EMAIL_AGENT_BACKSTORY = """You are a senior communications specialist with expertise in 
corporate communications and professional correspondence. Your strengths include:

- Crafting clear, engaging professional emails
- Adapting tone and style for different audiences
- Structuring information for maximum impact and readability
- Writing compelling subject lines that encourage opens
- Ensuring proper email etiquette and formatting

Your approach to professional email communication:
1. Open with a clear, professional greeting
2. State the purpose immediately
3. Present key information in a scannable format
4. Use bullet points and sections for clarity
5. Include a clear call-to-action if needed
6. Close professionally with appropriate sign-off

You understand that email is often the first impression an organization makes,
and you treat every message as an opportunity to demonstrate professionalism and value."""


def create_email_agent() -> Agent:
    """
    Create a configured Email Coordinator agent.
    
    Returns:
        Configured Agent instance for email coordination.
    """
    logger.info("Creating email coordinator agent")
    
    email_tool = create_email_tool()
    
    config = AgentConfig(
        role="Email Communication Specialist",
        goal="Compose and send professional, well-formatted research reports via email",
        backstory=EMAIL_AGENT_BACKSTORY,
        tools=[email_tool],
        max_iter=2,
        allow_delegation=False,
    )
    
    return AgentFactory.create_agent(config)
