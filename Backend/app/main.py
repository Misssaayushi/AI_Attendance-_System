from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import api_router
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_logger import log_requests_middleware
from app.database.connection import test_db_connection
from app.utils.logger import logger

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    logger.info("🚀 AI Attendance System Backend starting...")
    
    # 1. Test database connection
    if test_db_connection():
        logger.info("✅ Database connection: OK")
        
        # 2. Initialize tables
        from app.database.connection import init_db
        try:
            init_db()
        except Exception as e:
            logger.error(f"❌ Table initialization FAILED: {str(e)}")
    else:
        logger.error("❌ Database connection: FAILED - Tables not initialized")
    
    yield  # --- Server is running ---
    
    # --- Shutdown Logic ---
    logger.info("🛑 Backend shutting down...")

def create_app() -> FastAPI:
    """FastAPI application factory."""
    
    app = FastAPI(
        title="AI Attendance System API",
        description="Backend API for AI-Based Smart Attendance Management System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        debug=settings.DEBUG_MODE,
        lifespan=lifespan
    )

    # Register middleware
    app.middleware("http")(log_requests_middleware)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"], # React dev servers
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register modular routers
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # Register global error handlers
    register_error_handlers(app)

    @app.get("/")
    async def root():
        """Root endpoint to verify server status."""
        return {
            "system": "AI Attendance System",
            "status": "running",
            "version": "1.0.0",
            "docs": "/docs"
        }

    return app

# Main app instance
app = create_app()
