"""
Configuration settings for Code Weaver application.
"""

import os
from typing import Optional


class Settings:
    """Application settings with environment variable support."""
    
    # Neo4j Database settings
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # Server settings
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    
    # Analysis settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "1048576"))  # 1MB
    EXCLUDED_DIRS: list = [
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules",
        ".pytest_cache",
        ".coverage",
        "build",
        "dist",
        "*.egg-info"
    ]
    
    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")


# Global settings instance
settings = Settings()
