"""
Input Validation Utilities for AI Research Crew Pro

Provides validation functions for user inputs with
detailed error messages and sanitization.
"""

import re
from dataclasses import dataclass
from typing import Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, field: str, message: str, value: Optional[str] = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    value: str
    error: Optional[str] = None


def validate_email(email: str) -> ValidationResult:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate.
        
    Returns:
        ValidationResult with sanitized email or error message.
    """
    if not email:
        return ValidationResult(
            is_valid=False,
            value="",
            error="Email address is required"
        )
    
    # Basic sanitization
    email = email.strip().lower()
    
    # Email regex pattern (RFC 5322 simplified)
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return ValidationResult(
            is_valid=False,
            value=email,
            error="Invalid email format. Please enter a valid email address."
        )
    
    # Check for common typos
    common_domains = {
        "gmial.com": "gmail.com",
        "gmal.com": "gmail.com",
        "gamil.com": "gmail.com",
        "yaho.com": "yahoo.com",
        "hotmal.com": "hotmail.com",
    }
    
    domain = email.split("@")[1]
    if domain in common_domains:
        suggested = email.replace(domain, common_domains[domain])
        return ValidationResult(
            is_valid=False,
            value=email,
            error=f"Did you mean '{suggested}'?"
        )
    
    return ValidationResult(is_valid=True, value=email)


def validate_topic(topic: str, min_length: int = 5, max_length: int = 500) -> ValidationResult:
    """
    Validate research topic input.
    
    Args:
        topic: Research topic to validate.
        min_length: Minimum topic length.
        max_length: Maximum topic length.
        
    Returns:
        ValidationResult with sanitized topic or error message.
    """
    if not topic:
        return ValidationResult(
            is_valid=False,
            value="",
            error="Research topic is required"
        )
    
    # Sanitize input
    topic = topic.strip()
    
    # Remove excessive whitespace
    topic = re.sub(r'\s+', ' ', topic)
    
    # Check length
    if len(topic) < min_length:
        return ValidationResult(
            is_valid=False,
            value=topic,
            error=f"Topic must be at least {min_length} characters long"
        )
    
    if len(topic) > max_length:
        return ValidationResult(
            is_valid=False,
            value=topic,
            error=f"Topic must be less than {max_length} characters"
        )
    
    # Check for potentially harmful patterns (basic XSS prevention)
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, topic, re.IGNORECASE):
            return ValidationResult(
                is_valid=False,
                value=topic,
                error="Topic contains invalid characters"
            )
    
    return ValidationResult(is_valid=True, value=topic)


def validate_num_results(value: int, min_val: int = 1, max_val: int = 20) -> ValidationResult:
    """
    Validate number of search results.
    
    Args:
        value: Number to validate.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.
        
    Returns:
        ValidationResult with the value or error message.
    """
    if value < min_val:
        return ValidationResult(
            is_valid=False,
            value=str(value),
            error=f"Value must be at least {min_val}"
        )
    
    if value > max_val:
        return ValidationResult(
            is_valid=False,
            value=str(value),
            error=f"Value must be at most {max_val}"
        )
    
    return ValidationResult(is_valid=True, value=str(value))
