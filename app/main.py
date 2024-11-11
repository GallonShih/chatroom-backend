import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
from routers.v1 import default, user, chat, websocket
from db.init_db import init_db
from utils.logger import logger

logger.info("Starting FastAPI application...")

cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

# Constants for configuration
API_PREFIX_V1 = "/api/v1"
SWAGGER_URL = f"{API_PREFIX_V1}/docs"
REDOC_URL = f"{API_PREFIX_V1}/redoc"
OPENAPI_URL = f"{API_PREFIX_V1}/openapi.json"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting up...")
    init_db()  # Initialize your database

    yield  # Your app runs here

    # Shutdown logic (if needed)
    logger.info("Shutting down...")

# Initialize the FastAPI app
app = FastAPI(
    title="Chatroom Backend API",
    description="This is the API documentation for the Chatroom Backend.",
    version="1.0.0",
    docs_url=SWAGGER_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
    lifespan=lifespan
)

# CORS middleware configuration for handling cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Or specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router with prefix
app.include_router(default.router, prefix=API_PREFIX_V1)
app.include_router(user.router, prefix=API_PREFIX_V1, tags=["User"])
app.include_router(chat.router, prefix=API_PREFIX_V1, tags=["Chat"])
app.include_router(websocket.router, prefix=API_PREFIX_V1, tags=["WebSocket"])

# Redirect root to Swagger documentation
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url=SWAGGER_URL)


# Main entry point for running the application
if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=8000, workers=5)
