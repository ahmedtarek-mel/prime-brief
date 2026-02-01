"""AI Research Crew Pro - Agents Module"""

from .base_agent import AgentFactory, AgentConfig
from .researcher import create_researcher_agent
from .summarizer import create_summarizer_agent
from .email_agent import create_email_agent

__all__ = [
    "AgentFactory",
    "AgentConfig",
    "create_researcher_agent",
    "create_summarizer_agent",
    "create_email_agent",
]
