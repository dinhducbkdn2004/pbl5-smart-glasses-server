import os

class Settings:
    MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN', 'DEFAULT_ACCESS_TOKEN')
    # DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./test.db')

settings = Settings()
