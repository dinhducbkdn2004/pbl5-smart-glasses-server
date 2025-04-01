from fastapi import FastAPI
from app.api.route import router
from app.core.config import settings
from app.core.logging import logger
from fastapi.middleware.cors import CORSMiddleware

# Khởi tạo FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins trong development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    logger.info(f"Server running on {settings.HOST}:{settings.PORT}")

@app.get("/")
async def index():
    logger.info("Root endpoint accessed")
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Bao gồm các route từ file route.py
app.include_router(router)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
