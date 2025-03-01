from fastapi import FastAPI
from app.api.route import router

# Khởi tạo FastAPI app
app = FastAPI()

@app.get("/")
async def index():
    return {"message": "Hello world from FastAPI"}


# Bao gồm các route từ file route.py
app.include_router(router)
