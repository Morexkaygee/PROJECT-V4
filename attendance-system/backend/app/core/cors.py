"""
CORS Configuration Module
Handles Cross-Origin Resource Sharing settings for the attendance system
"""
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import os


def get_cors_origins() -> List[str]:
    """
    Get CORS origins based on environment.
    Returns appropriate origins for development, staging, and production.
    """
    # Default development origins
    default_origins = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Check if we're in production
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        # In production, use only configured origins
        production_origins = os.getenv("PRODUCTION_CORS_ORIGINS", "").split(",")
        production_origins = [origin.strip() for origin in production_origins if origin.strip()]
        
        if production_origins:
            return production_origins
        else:
            # Fallback to settings if no production origins specified
            return settings.cors_origins
    
    elif environment == "staging":
        # In staging, allow staging domains
        staging_origins = os.getenv("STAGING_CORS_ORIGINS", "").split(",")
        staging_origins = [origin.strip() for origin in staging_origins if origin.strip()]
        
        if staging_origins:
            return staging_origins + default_origins
        else:
            return settings.cors_origins + default_origins
    
    else:
        # Development environment - use configured origins
        return settings.cors_origins


def get_cors_methods() -> List[str]:
    """Get allowed CORS methods."""
    return ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]


def get_cors_headers() -> List[str]:
    """Get allowed CORS headers."""
    return [
        "Accept",
        "Accept-Language",
        "Content-Language", 
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "X-CSRF-Token",
        "X-API-Key"
    ]


def get_exposed_headers() -> List[str]:
    """Get headers to expose to the client."""
    return [
        "Content-Length",
        "Content-Type",
        "X-Total-Count",
        "X-Page-Count"
    ]


def configure_cors(app) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    origins = get_cors_origins()
    
    # Log CORS configuration for debugging
    print(f"CORS Origins: {origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=get_cors_methods(),
        allow_headers=get_cors_headers(),
        expose_headers=get_exposed_headers(),
        max_age=3600,  # Cache preflight requests for 1 hour
    )


def is_origin_allowed(origin: str) -> bool:
    """
    Check if an origin is allowed for CORS.
    
    Args:
        origin: The origin to check
        
    Returns:
        bool: True if origin is allowed, False otherwise
    """
    allowed_origins = get_cors_origins()
    return origin in allowed_origins


# CORS configuration for different environments
CORS_CONFIG = {
    "development": {
        "origins": [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000", 
            "http://127.0.0.1:3001"
        ],
        "credentials": True,
        "methods": ["*"],
        "headers": ["*"]
    },
    "staging": {
        "origins": [
            "https://staging-attendance.futa.edu.ng",
            "http://localhost:3000",
            "http://localhost:3001"
        ],
        "credentials": True,
        "methods": get_cors_methods(),
        "headers": get_cors_headers()
    },
    "production": {
        "origins": [
            "https://attendance.futa.edu.ng",
            "https://www.attendance.futa.edu.ng"
        ],
        "credentials": True,
        "methods": get_cors_methods(),
        "headers": get_cors_headers()
    }
}