from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    # Base settings
    PROJECT_NAME: str = "Smart Glasses Navigation Server"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # OpenStreetMap settings
    OSRM_URL: str = "http://router.project-osrm.org/route/v1/foot"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"
    USER_AGENT: str = "SmartGlassesNavigationApp/1.0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # API Keys
    GOOGLE_MAPS_API_KEY: str = ""
    
    # Safety configurations
    OBSTACLE_THRESHOLD: float = 1.5  # meters
    DIRECTION_CHANGE_THRESHOLD: float = 45  # degrees

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
