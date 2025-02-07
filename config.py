from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Mapbox configuration
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Validate required environment variables
if not MAPBOX_ACCESS_TOKEN:
    raise ValueError("MAPBOX_ACCESS_TOKEN environment variable is required")