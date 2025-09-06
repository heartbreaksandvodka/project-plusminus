"""
Configuration management for EA Service
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """EA Service configuration settings"""
    
    # Service configuration
    host: str = "127.0.0.1"
    port: int = 8001
    debug: bool = True
    
    # Django backend integration
    django_backend_url: str = "http://127.0.0.1:8000"
    django_api_base: str = "http://127.0.0.1:8000/api"
    
    # CORS configuration
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # JWT configuration (should match Django settings)
    jwt_secret_key: str = "your-secret-key-here"  # Should match Django SECRET_KEY
    jwt_algorithm: str = "HS256"
    
    # EA Management configuration
    algorithms_dir: str = "../ALGORITHMSMT5EA"
    max_concurrent_eas: int = 10
    ea_timeout_seconds: int = 30
    
    # Process management
    process_check_interval: int = 5  # seconds
    cleanup_interval: int = 60  # seconds
    
    # WebSocket configuration
    websocket_ping_interval: int = 30
    websocket_ping_timeout: int = 10
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "ea_service.log"
    
    class Config:
        env_prefix = "EA_SERVICE_"
        env_file = ".env"

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
