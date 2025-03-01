from fastapi import FastAPI
from app.api.route import router

# Khởi tạo FastAPI app
app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Server listening on port 8000"}


# Bao gồm các route từ file route.py
app.include_router(router)
