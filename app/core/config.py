class Settings():
    """Application settings"""
    APP_NAME: str = "Smart Glasses Navigation"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # OpenStreetMap configurations
    OSRM_URL: str = "http://router.project-osrm.org/route/v1/foot"
    NOMINATIM_URL: str = "https://nominatim.openstreetmap.org/search"
    USER_AGENT: str = "SmartGlassesNavigationApp/1.0"

    # Safety configurations
    OBSTACLE_THRESHOLD: float = 1.5  # meters
    DIRECTION_CHANGE_THRESHOLD: float = 45  # degrees

    class Config:
        env_file = ".env"

settings = Settings()
