# app/routers/v1/default.py

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from utils.logger import logger

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    Returns a JSON response indicating the service is healthy.
    """
    logger.info("health_check")
    return JSONResponse(
        content={"status": "healthy"},
        status_code=status.HTTP_200_OK
    )
