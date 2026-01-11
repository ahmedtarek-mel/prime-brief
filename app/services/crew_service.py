"""
Crew Orchestration Service for AI Research Crew Pro

Provides high-level orchestration of the multi-agent research
workflow with progress tracking and result handling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Callable, Any
from crewai import Crew

from app.config.settings import get_settings, setup_crewai_environment
from app.agents import (
    create_researcher_agent,
    create_summarizer_agent,
    create_email_agent,
)
from app.tasks import (
    create_research_task,
    create_summarization_task,
    create_email_task,
)
from app.utils.logger import get_logger, TaskLogger

logger = get_logger(__name__)


@dataclass
class ResearchResult:
    """Container for research workflow results."""
    success: bool
    research_output: Optional[str] = None
    summary_output: Optional[str] = None
    email_output: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_task_outputs(self) -> List[str]:
        """Get list of all task outputs."""
        outputs = []
        if self.research_output:
            outputs.append(self.research_output)
        if self.summary_output:
            outputs.append(self.summary_output)
        if self.email_output:
            outputs.append(self.email_output)
        return outputs


class CrewService:
    """
    Orchestrates the multi-agent research workflow.
    
    Coordinates between researcher, summarizer, and email agents
    to execute the complete research-to-report pipeline.
    """
    
    def __init__(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """
        Initialize the crew service.
        
        Args:
            progress_callback: Optional callback for progress updates.
                              Receives (percentage, message) arguments.
        """
        self.progress_callback = progress_callback
        self._task_logger = TaskLogger("crew_service")
        
        # Ensure CrewAI environment is configured
        setup_crewai_environment()
    
    def _update_progress(self, percentage: int, message: str):
        """Update progress via callback if available."""
        if self.progress_callback:
            self.progress_callback(percentage, message)
        self._task_logger.progress(message, percentage)
    
    def execute_research_workflow(
        self,
        topic: str,
        recipient_email: str,
        report_format: str = "Summary Report",
        num_results: int = 5,
    ) -> ResearchResult:
        """
        Execute the complete research workflow.
        
        Args:
            topic: Research topic to investigate.
            recipient_email: Email address to send report to.
            report_format: Format for the final report.
            num_results: Number of search results to gather.
            
        Returns:
            ResearchResult with all outputs or error information.
        """
        start_time = datetime.now()
        self._task_logger.start(f"Starting research workflow for: {topic[:50]}...")
        
        try:
            # Phase 1: Create agents
            self._update_progress(10, "Assembling AI research team...")
            
            researcher = create_researcher_agent(topic, num_results)
            summarizer = create_summarizer_agent(report_format)
            email_agent = create_email_agent()
            
            # Phase 2: Create tasks
            self._update_progress(25, "Configuring research tasks...")
            
            research_task = create_research_task(
                agent=researcher,
                topic=topic,
                num_results=num_results,
            )
            
            summarization_task = create_summarization_task(
                agent=summarizer,
                report_format=report_format,
                research_task=research_task,
            )
            
            email_task = create_email_task(
                agent=email_agent,
                recipient_email=recipient_email,
                topic=topic,
                report_format=report_format,
                summarization_task=summarization_task,
            )
            
            # Phase 3: Assemble and run crew
            self._update_progress(40, "Initiating research process...")
            
            settings = get_settings()
            
            crew = Crew(
                agents=[researcher, summarizer, email_agent],
                tasks=[research_task, summarization_task, email_task],
                verbose=settings.enable_verbose,
                memory=settings.enable_memory,
                max_rpm=settings.max_rpm,
            )
            
            self._update_progress(50, "AI agents working on research...")
            
            # Execute the crew
            result = crew.kickoff()
            
            self._update_progress(90, "Finalizing results...")
            
            # Extract task outputs
            research_output = None
            summary_output = None
            email_output = None
            
            if hasattr(result, 'tasks_output') and result.tasks_output:
                if len(result.tasks_output) > 0:
                    research_output = result.tasks_output[0].raw
                if len(result.tasks_output) > 1:
                    summary_output = result.tasks_output[1].raw
                if len(result.tasks_output) > 2:
                    email_output = result.tasks_output[2].raw
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_progress(100, "Research complete!")
            self._task_logger.success(f"Workflow completed in {execution_time:.2f}s")
            
            return ResearchResult(
                success=True,
                research_output=research_output,
                summary_output=summary_output,
                email_output=email_output,
                execution_time=execution_time,
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_message = str(e)
            
            self._task_logger.error("Workflow failed", e)
            
            return ResearchResult(
                success=False,
                error_message=error_message,
                execution_time=execution_time,
            )
    
    def validate_configuration(self) -> dict:
        """
        Validate that all required configuration is present.
        
        Returns:
            Dict with validation status for each component.
        """
        settings = get_settings()
        return settings.validate_required_keys()
    
    def get_missing_configuration(self) -> List[str]:
        """
        Get list of missing required configuration.
        
        Returns:
            List of missing configuration key names.
        """
        settings = get_settings()
        return settings.get_missing_keys()
