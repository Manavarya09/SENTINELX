"""
Configuration settings for SentinelX backend.
Uses Pydantic for validation and environment variable loading.
"""

from pydantic import BaseSettings, Field
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings with validation."""

    # Database
    database_url: str = Field(default="postgresql://sentinelx:password@localhost:5432/sentinelx", env="DATABASE_URL")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")

    # JWT
    jwt_secret_key: str = Field(default="your-secret-key-change-in-production", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration_hours: int = Field(default=24)

    # Security thresholds
    brute_force_threshold: int = Field(default=5, description="Failed login attempts before blocking")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    rate_limit_max_requests: int = Field(default=100, description="Max requests per window")

    # Attack detection
    sql_injection_keywords: List[str] = Field(default=[
        "union", "select", "insert", "update", "delete", "drop", "create",
        "alter", "exec", "execute", "script", "javascript", "vbscript"
    ])
    xss_patterns: List[str] = Field(default=[
        "<script", "javascript:", "onload=", "onerror=", "onclick="
    ])

    # CORS
    cors_origins: List[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])

    # Optional ML
    enable_ml_anomaly: bool = Field(default=False)
    ml_model_path: Optional[str] = Field(default=None)

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()