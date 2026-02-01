"""
Base Agent Factory for AI Research Crew Pro

Provides factory pattern for creating configured CrewAI agents
with shared LLM configuration and common settings.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any
from crewai import Agent, LLM

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentConfig:
    """Configuration dataclass for agent creation."""
    role: str
    goal: str
    backstory: str
    tools: List[Any] = field(default_factory=list)
    verbose: bool = True
    max_iter: int = 5
    allow_delegation: bool = False


class AgentFactory:
    """
    Factory for creating configured CrewAI agents.
    
    Provides centralized agent creation with shared LLM
    configuration and consistent settings.
    """
    
    _llm_instance: Optional[LLM] = None
    
    @classmethod
    def get_llm(cls) -> LLM:
        """
        Get or create cached LLM instance.
        
        Returns:
            Configured LLM instance based on settings.
        """
        if cls._llm_instance is None:
            settings = get_settings()
            
            logger.info(f"Initializing LLM: {settings.llm_provider}")
            
            cls._llm_instance = LLM(
                model=settings.current_model,
                temperature=settings.llm_temperature,
                max_retries=5,
            )
        
        return cls._llm_instance
    
    @classmethod
    def reset_llm(cls):
        """Reset the cached LLM instance (useful for testing)."""
        cls._llm_instance = None
    
    @classmethod
    def create_agent(cls, config: AgentConfig) -> Agent:
        """
        Create a CrewAI agent from configuration.
        
        Args:
            config: AgentConfig with agent settings.
            
        Returns:
            Configured Agent instance.
        """
        settings = get_settings()
        
        logger.debug(f"Creating agent: {config.role}")
        
        agent = Agent(
            role=config.role,
            goal=config.goal,
            backstory=config.backstory,
            tools=config.tools,
            llm=cls.get_llm(),
            verbose=settings.enable_verbose and config.verbose,
            max_iter=settings.max_agent_iterations or config.max_iter,
            allow_delegation=config.allow_delegation,
        )
        
        logger.info(f"Created agent: {config.role}")
        return agent
