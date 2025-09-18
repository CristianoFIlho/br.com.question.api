from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.routers import quiz, auth
from app.database.session import engine
from app.models.database import Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="API para o sistema de simulados Salesforce",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=settings.API_V1_STR,
    tags=["authentication"]
)

app.include_router(
    quiz.router,
    prefix=settings.API_V1_STR,
    tags=["quiz"]
)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Salesforce Quiz API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "Something went wrong. Please try again later."
        }
    )
