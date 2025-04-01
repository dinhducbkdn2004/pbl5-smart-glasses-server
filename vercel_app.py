from mangum import Mangum
from app.main import app

# Create Mangum handler with custom settings
handler = Mangum(app, lifespan="off") 