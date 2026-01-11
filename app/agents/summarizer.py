"""
Content Summarizer Agent for AI Research Crew Pro

Specialized agent for analyzing research findings and creating
structured, actionable summaries in various formats.
"""

from typing import Literal
from crewai import Agent

from .base_agent import AgentFactory, AgentConfig
from app.utils.logger import get_logger

logger = get_logger(__name__)


ReportFormat = Literal["Summary Report", "Detailed Analysis", "Executive Brief"]


SUMMARIZER_BACKSTORY = """You are a world-class content analyst and strategic communicator 
with extensive experience in business intelligence and executive reporting. Your expertise includes:

- Transforming complex research data into clear, actionable insights
- Identifying key patterns, trends, and implications
- Structuring information for different audiences and purposes
- Writing compelling narratives that highlight critical findings
- Providing strategic recommendations based on data analysis

Your approach to content analysis:
1. Review all research findings comprehensively
2. Identify the most significant and actionable insights
3. Organize information in a logical, hierarchical structure
4. Highlight implications and potential impacts
5. Craft recommendations based on evidence

You excel at making complex information accessible and actionable,
always tailoring your communication style to the intended format and audience."""


FORMAT_REQUIREMENTS = {
    "Summary Report": """
Create a concise summary with:
- Key Findings (3-5 bullet points)
- Main trends and developments
- Actionable insights
- Source references
""",
    "Detailed Analysis": """
Create a comprehensive analysis with:
- Executive overview
- Detailed findings with supporting evidence
- Trend analysis and implications
- Expert opinions and perspectives
- Strategic recommendations
- Complete source citations
""",
    "Executive Brief": """
Create a one-page executive brief with:
- Critical headline findings
- Business implications
- Immediate recommendations
- Risk factors (if any)
- Key takeaways for leadership
""",
}


def create_summarizer_agent(
    report_format: ReportFormat = "Summary Report"
) -> Agent:
    """
    Create a configured Content Summarizer agent.
    
    Args:
        report_format: The format for the final report.
        
    Returns:
        Configured Agent instance for content summarization.
    """
    logger.info(f"Creating summarizer agent with format: {report_format}")
    
    format_requirements = FORMAT_REQUIREMENTS.get(report_format, FORMAT_REQUIREMENTS["Summary Report"])
    
    config = AgentConfig(
        role="Content Analysis & Summarization Expert",
        goal=f"Create an exceptional {report_format} that transforms research data into actionable insights",
        backstory=SUMMARIZER_BACKSTORY + f"\n\nCurrent Task Requirements:{format_requirements}",
        tools=[],  # No external tools needed - works with internal context
        max_iter=3,
        allow_delegation=False,
    )
    
    return AgentFactory.create_agent(config)
