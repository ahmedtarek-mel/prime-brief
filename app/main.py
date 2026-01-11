"""
AI Research Crew Pro - Main Application

Streamlit-based web interface for the multi-agent
research and reporting system.
"""

import streamlit as st
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from app.config.settings import get_settings
from app.services import CrewService
from app.utils import validate_email, validate_topic, setup_logging
from app.ui import (
    get_custom_css,
    render_header,
    render_config_panel,
    render_features_panel,
    render_results,
    render_download_buttons,
    render_configuration_warning,
    render_footer,
)



def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Prime Brief",
        page_icon="assets/logo.png",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # Inject custom CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)


def check_configuration() -> bool:
    """
    Check if required configuration is present.
    
    Returns:
        True if configuration is valid, False otherwise.
    """
    crew_service = CrewService()
    missing_keys = crew_service.get_missing_configuration()
    
    if missing_keys:
        render_configuration_warning(missing_keys)
        return False
    
    return True


def run_research(config: dict):
    """
    Execute the research workflow with progress updates.
    
    Args:
        config: Dictionary with research configuration.
    """
    # Validate inputs
    email_result = validate_email(config["recipient_email"])
    if not email_result.is_valid:
        st.error(f"Invalid email: {email_result.error}")
        return
    
    topic_result = validate_topic(config["topic"])
    if not topic_result.is_valid:
        st.error(f"Invalid topic: {topic_result.error}")
        return
    
    # Create progress container
    progress_container = st.empty()
    status_container = st.empty()
    
    def update_progress(percentage: int, message: str):
        """Callback for progress updates."""
        progress_container.progress(percentage / 100)
        status_container.info(f"{message}")
    
    # Initialize crew service with progress callback
    crew_service = CrewService(progress_callback=update_progress)
    
    # Execute research
    with st.spinner("AI research team is working..."):
        result = crew_service.execute_research_workflow(
            topic=topic_result.value,
            recipient_email=email_result.value,
            report_format=config["report_format"],
            num_results=config["num_results"],
        )
    
    # Clear progress indicators
    progress_container.empty()
    status_container.empty()
    
    # Store result in session state
    st.session_state.result = result
    st.session_state.topic = config["topic"]


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    
    # Configure page
    setup_page()
    
    # Render header
    render_header()
    
    # Check configuration
    if not check_configuration():
        return
    
    # Main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Configuration panel
        config = render_config_panel()
        
        # Run button
        run_button = st.button(
            "Launch Research Crew",
            use_container_width=True,
            help="Start the AI research process"
        )
    
    with col2:
        # Features panel
        render_features_panel()
    
    # Handle research execution
    if run_button:
        if not config["topic"] or not config["recipient_email"]:
            st.error("Please fill in all required fields!")
        else:
            run_research(config)
    
    # Display results if available
    if "result" in st.session_state:
        st.markdown("---")
        render_results(st.session_state.result)
        render_download_buttons(
            st.session_state.result, 
            st.session_state.get("topic", "research")
        )
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main()
