"""
Research Tasks for AI Research Crew Pro

Defines structured task templates for the multi-agent
research and reporting workflow.
"""

from typing import Optional, List
from crewai import Agent, Task

from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_research_task(
    agent: Agent,
    topic: str,
    num_results: int = 5,
    focus_areas: Optional[List[str]] = None
) -> Task:
    """
    Create a web research task.
    
    Args:
        agent: The researcher agent to assign.
        topic: Research topic.
        num_results: Number of sources to gather.
        focus_areas: Optional specific areas to focus on.
        
    Returns:
        Configured Task for web research.
    """
    logger.info(f"Creating research task for: {topic[:50]}...")
    
    focus_section = ""
    if focus_areas:
        focus_section = f"\n\nFocus Areas:\n" + "\n".join(f"- {area}" for area in focus_areas)
    
    description = f"""
Conduct comprehensive web research on: {topic}

Research Requirements:
1. Search for the most current and relevant information
2. Focus on credible, authoritative sources
3. Gather information from at least {num_results} different perspectives or sources
4. Include:
   - Current trends and developments
   - Expert opinions and analysis
   - Key statistics and data points
   - Recent news and announcements
5. Note publication dates and assess source credibility
6. Look for both supporting and contrasting viewpoints
{focus_section}

Quality Standards:
- Prioritize recency (prefer sources from the last 12 months)
- Verify key facts across multiple sources when possible
- Include direct quotes from experts where available
- Note any limitations or gaps in available information

Provide detailed findings with proper source citations.
"""

    expected_output = f"""
A comprehensive research report containing:
- {num_results}+ credible sources with full citations
- Key findings organized by theme
- Current trends and developments
- Expert insights and opinions
- Data and statistics (with sources)
- Publication dates for all sources
"""

    return Task(
        description=description.strip(),
        expected_output=expected_output.strip(),
        agent=agent,
    )


def create_summarization_task(
    agent: Agent,
    report_format: str,
    research_task: Task
) -> Task:
    """
    Create a content summarization task.
    
    Args:
        agent: The summarizer agent to assign.
        report_format: Format for the final report.
        research_task: The research task to use as context.
        
    Returns:
        Configured Task for summarization.
    """
    logger.info(f"Creating summarization task with format: {report_format}")
    
    format_instructions = {
        "Summary Report": """
Structure your report as:
1. **Executive Summary** (2-3 sentences)
2. **Key Findings** (3-5 bullet points with brief explanations)
3. **Current Trends** (What's happening now)
4. **Actionable Insights** (What this means for the reader)
5. **Sources** (List of references used)
""",
        "Detailed Analysis": """
Structure your report as:
1. **Executive Overview** (1 paragraph summary)
2. **Background & Context** (Why this matters)
3. **Detailed Findings** (Organized by theme with supporting evidence)
4. **Trend Analysis** (Patterns and trajectories)
5. **Expert Perspectives** (What thought leaders say)
6. **Implications & Recommendations** (What to do with this information)
7. **Appendix: Sources & Methodology**
""",
        "Executive Brief": """
Structure your report as:
1. **Bottom Line Up Front** (The single most important takeaway)
2. **Critical Findings** (3 bullet points maximum)
3. **Business Impact** (Why leadership should care)
4. **Recommended Actions** (Next steps)
5. **Key Sources** (2-3 most credible references)

Keep the entire brief to one page maximum.
"""
    }
    
    instructions = format_instructions.get(report_format, format_instructions["Summary Report"])
    
    description = f"""
Analyze the research findings and create a {report_format}.

Your Task:
1. Review all research findings provided
2. Identify the most significant and actionable insights
3. Synthesize information from multiple sources
4. Create a well-structured {report_format}
5. Ensure the output is professional and actionable

{instructions}

Writing Guidelines:
- Use clear, professional language
- Avoid jargon unless necessary (explain when used)
- Make the content scannable with headers and bullets
- Highlight surprising or particularly important findings
- Be objective and balanced in your analysis
- Use Markdown formatting for structure
"""

    expected_output = f"""
A professionally formatted {report_format} in Markdown with:
- Clear structure and organization
- Key insights prominently featured
- Actionable takeaways
- Proper source attribution
- Professional tone suitable for email delivery
"""

    return Task(
        description=description.strip(),
        expected_output=expected_output.strip(),
        agent=agent,
        context=[research_task],
    )


def create_email_task(
    agent: Agent,
    recipient_email: str,
    topic: str,
    report_format: str,
    summarization_task: Task
) -> Task:
    """
    Create an email delivery task.
    
    Args:
        agent: The email agent to assign.
        recipient_email: Email address to send to.
        topic: The research topic (for subject line).
        report_format: Type of report being sent.
        summarization_task: The summarization task for context.
        
    Returns:
        Configured Task for email delivery.
    """
    logger.info(f"Creating email task for recipient: {recipient_email}")
    
    description = f"""
Send a professional email with the research report to: {recipient_email}

Email Requirements:
1. Subject Line: "AI Research Report: {topic} - {report_format}"
2. Opening: Professional greeting
3. Introduction: Brief explanation of what this report contains
4. Body: The complete research summary/analysis
5. Closing: Professional sign-off with note about AI research methodology
6. Format: Use Markdown formatting (it will be converted to HTML)

Email Best Practices:
- Keep the introduction brief (2-3 sentences)
- Let the research content be the focus
- Include a call-to-action if appropriate (e.g., "reply with questions")
- Maintain a helpful, professional tone
- Don't over-explain the AI methodology

Send the email and confirm successful delivery.
"""

    expected_output = f"""
Confirmation that:
1. Email was composed with proper formatting
2. Email was successfully sent to {recipient_email}
3. Subject line follows the specified format
4. Content includes the full research summary
"""

    return Task(
        description=description.strip(),
        expected_output=expected_output.strip(),
        agent=agent,
        context=[summarization_task],
    )
