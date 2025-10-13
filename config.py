"""
Configuration management for Canvas MCP Worker.
Handles environment variables and application settings.
"""

from typing import Optional
from pydantic import BaseModel, Field
import os


class Config(BaseModel):
    """Application configuration loaded from environment variables."""

    # Canvas API Configuration (provided per-request)
    # These are NOT loaded from env since they come from the request

    # Application Settings
    default_per_page: int = Field(default=100, description="Default pagination size")
    max_per_page: int = Field(default=100, description="Maximum pagination size")
    request_timeout: int = Field(default=30, description="HTTP request timeout in seconds")

    # Feature Flags
    enable_caching: bool = Field(default=False, description="Enable response caching")
    enable_debug: bool = Field(default=False, description="Enable debug logging")

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            default_per_page=int(os.getenv("DEFAULT_PER_PAGE", "100")),
            max_per_page=int(os.getenv("MAX_PER_PAGE", "100")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            enable_caching=os.getenv("ENABLE_CACHING", "false").lower() == "true",
            enable_debug=os.getenv("ENABLE_DEBUG", "false").lower() == "true",
        )


# Global config instance
config = Config.from_env()
