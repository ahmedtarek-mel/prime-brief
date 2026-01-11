"""
Configuration Management for AI Research Crew Pro

This module provides centralized configuration management using Pydantic
for type-safe settings with environment variable loading.
"""

import os
from typing import Literal, Optional
from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation and defaults."""
    
    # LLM Configuration
    google_api_key: Optional[str] = Field(None, alias="GOOGLE_API_KEY")
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    llm_provider: Literal["gemini", "openai"] = Field("gemini", alias="LLM_PROVIDER")
    gemini_model: str = Field("gemini/gemini-2.5-flash", alias="GEMINI_MODEL")
    openai_model: str = Field("gpt-4-turbo-preview", alias="OPENAI_MODEL")
    llm_temperature: float = Field(0.7, alias="LLM_TEMPERATURE", ge=0.0, le=2.0)
    
    # Search Configuration
    serper_api_key: Optional[str] = Field(None, alias="SERPER_API_KEY")
    
    # Email Configuration
    email_user: Optional[str] = Field(None, alias="EMAIL_USER")
    email_pass: Optional[str] = Field(None, alias="EMAIL_PASS")
    smtp_server: str = Field("smtp.gmail.com", alias="SMTP_SERVER")
    smtp_port: int = Field(587, alias="SMTP_PORT")
    
    # Application Settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        "INFO", alias="LOG_LEVEL"
    )
    enable_memory: bool = Field(True, alias="ENABLE_MEMORY")
    enable_verbose: bool = Field(True, alias="ENABLE_VERBOSE")
    max_agent_iterations: int = Field(5, alias="MAX_AGENT_ITERATIONS", ge=1, le=20)
    max_rpm: int = Field(4, alias="MAX_RPM", ge=1)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    @field_validator("llm_temperature", mode="before")
    @classmethod
    def validate_temperature(cls, v):
        """Ensure temperature is a valid float."""
        if isinstance(v, str):
            return float(v)
        return v
    
    @property
    def current_model(self) -> str:
        """Get the model name based on selected provider."""
        if self.llm_provider == "openai":
            return self.openai_model
        return self.gemini_model
    
    @property
    def current_api_key(self) -> Optional[str]:
        """Get the API key for the selected provider."""
        if self.llm_provider == "openai":
            return self.openai_api_key
        return self.google_api_key
    
    def validate_required_keys(self) -> dict[str, bool]:
        """Check which required API keys are configured."""
        return {
            "llm": self.current_api_key is not None,
            "search": self.serper_api_key is not None,
            "email": self.email_user is not None and self.email_pass is not None,
        }
    
    def get_missing_keys(self) -> list[str]:
        """Return list of missing required configuration keys."""
        missing = []
        validation = self.validate_required_keys()
        
        if not validation["llm"]:
            key_name = "OPENAI_API_KEY" if self.llm_provider == "openai" else "GOOGLE_API_KEY"
            missing.append(key_name)
        if not validation["search"]:
            missing.append("SERPER_API_KEY")
        if not validation["email"]:
            if not self.email_user:
                missing.append("EMAIL_USER")
            if not self.email_pass:
                missing.append("EMAIL_PASS")
        
        return missing


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings loaded from environment.
    """
    return Settings()


def setup_crewai_environment():
    """Configure environment variables required by CrewAI."""
    settings = get_settings()
    
    # Set CrewAI-specific environment variables
    os.environ["CREWAI_EMBEDDING_PROVIDER"] = "local"
    os.environ["CREWAI_EMBEDDING_MODEL"] = "sentence-transformers/all-MiniLM-L6-v2"
    os.environ["CHROMA_OPENAI_API_KEY"] = "fake-key"
    os.environ["CREWAI_STORAGE_DISABLED"] = "true"
    
    # Set API keys for LLM
    if settings.google_api_key:
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    if settings.serper_api_key:
        os.environ["SERPER_API_KEY"] = settings.serper_api_key
