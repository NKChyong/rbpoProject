"""Main FastAPI application."""

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.adapters.database import close_db, init_db
from app.api.v1 import auth, entries
from app.core.config import settings
from app.core.logging import add_request_id, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Secure Reading List API for tracking books, articles, and other content",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request_id middleware
app.middleware("http")(add_request_id)


# Custom error response model
class ApiError(Exception):
    """Custom API error exception."""

    def __init__(self, code: str, message: str, status: int = 400, details: Optional[dict] = None):
        """Initialize API error."""
        self.code = code
        self.message = message
        self.status = status
        self.details = details


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    """Handle custom API errors."""
    return JSONResponse(
        status_code=exc.status,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": exc.detail,
                "details": None,
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_server_error",
                "message": "An unexpected error occurred",
                "details": None,
            }
        },
    )


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize application on startup."""
    logger.info("Starting application...")
    await init_db()
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shut down successfully")


@app.get("/health")
async def health() -> dict[str, str]:
    """
    Health check endpoint.

    Returns application status.
    """
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns API information.
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(entries.router, prefix="/api/v1")
