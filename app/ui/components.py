"""
UI Components for AI Research Crew Pro

Provides reusable Streamlit components for building
the application interface.
"""

import streamlit as st
from typing import Optional, List

from app.services import ResearchResult


def render_header():
    """Render the main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>Prime Brief</h1>
        <p>Intelligence, Refined. Decisions, Defined.</p>
        <p class="subtitle">Powered by CrewAI & Google Gemini</p>
    </div>
    """, unsafe_allow_html=True)


def render_config_panel() -> dict:
    """
    Render the research configuration panel.
    
    Returns:
        Dictionary with user configuration values.
    """
    with st.expander("🔧 Research Configuration", expanded=True):
        topic = st.text_input(
            "Research Topic",
            placeholder="Enter the topic you want to research...",
            help="Be specific for better results. E.g., 'Latest AI developments in healthcare 2025'"
        )
        
        recipient_email = st.text_input(
            "Email Recipient",
            placeholder="recipient@example.com",
            help="Where to send the research report"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_results = st.slider(
                "Number of Sources",
                min_value=3,
                max_value=10,
                value=3,
                help="How many web sources to gather"
            )
        
        with col2:
            report_format = st.selectbox(
                "Report Format",
                options=["Summary Report", "Detailed Analysis", "Executive Brief"],
                help="Choose the format for your final report"
            )
    
    return {
        "topic": topic,
        "recipient_email": recipient_email,
        "num_results": num_results,
        "report_format": report_format,
    }


def render_features_panel():
    """Render the features information panel."""
    st.markdown("""
    <div class="status-card">
        <h3>Features</h3>
        <ul class="feature-list">
            <li>Multi-source web research</li>
            <li>AI-powered summarization</li>
            <li>Automated email delivery</li>
            <li>Multiple report formats</li>
            <li>Source verification</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def render_configuration_warning(missing_keys: List[str]):
    """
    Render a warning about missing configuration.
    
    Args:
        missing_keys: List of missing configuration keys.
    """
    st.markdown("""
    <div class="warning-box">
        <h4>Configuration Required</h4>
        <p>Please configure the following environment variables to use this application:</p>
    </div>
    """, unsafe_allow_html=True)
    
    for key in missing_keys:
        st.code(key)
    
    st.info(
        "Copy `env_template.txt` to `.env` and fill in your API keys. "
        "See the README for detailed setup instructions."
    )


def render_results(result: ResearchResult):
    """
    Render research results in tabs.
    
    Args:
        result: The ResearchResult from the crew service.
    """
    if not result.success:
        st.error(f"Research failed: {result.error_message}")
        st.info("Please check your API keys and internet connection, then try again.")
        return
    
    # Success notification
    st.balloons()
    st.success(f"Research completed in {result.execution_time:.1f} seconds!")
    
    # Results tabs
    tab1, tab2, tab3 = st.tabs([
        "Research Findings",
        "Analysis Summary", 
        "Email Status"
    ])
    
    with tab1:
        if result.research_output:
            st.subheader("Web Research Results")
            st.markdown(result.research_output)
        else:
            st.info("No research results available")
    
    with tab2:
        if result.summary_output:
            st.subheader("Content Analysis")
            st.markdown(result.summary_output)
        else:
            st.info("No summary available")
    
    with tab3:
        if result.email_output:
            st.subheader("Email Delivery Status")
            st.markdown(result.email_output)
        else:
            st.info("No email status available")


def render_download_buttons(result: ResearchResult, topic: str):
    """
    Render download buttons for research outputs.
    
    Args:
        result: The ResearchResult from the crew service.
        topic: The research topic (for filename).
    """
    if not result.success:
        return
    
    st.subheader("Download Reports")
    col1, col2 = st.columns(2)
    
    # Sanitize topic for filename
    safe_topic = "".join(c if c.isalnum() or c in " -_" else "_" for c in topic)
    safe_topic = safe_topic[:50].strip()
    
    with col1:
        if result.research_output:
            st.download_button(
                label="Download Research Report",
                data=result.research_output,
                file_name=f"research_report_{safe_topic}.md",
                mime="text/markdown",
                use_container_width=True,
            )
    
    with col2:
        if result.summary_output:
            st.download_button(
                label="Download Summary",
                data=result.summary_output,
                file_name=f"summary_{safe_topic}.md",
                mime="text/markdown",
                use_container_width=True,
            )


def render_footer():
    """Render the application footer."""
    st.markdown("""
    <div class="footer">
        <p>Prime Brief • Powered by CrewAI and Google Gemini</p>
        <p>Built with ❤️ for automated research and reporting</p>
    </div>
    """, unsafe_allow_html=True)
