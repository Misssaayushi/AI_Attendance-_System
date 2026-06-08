from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import test_db_connection
from app.middleware.error_handler import register_error_handlers
from app.middleware.request_logger import log_requests_middleware
from app.middleware.security_hardening import security_hardening_middleware
from app.routes import api_router
from app.scheduler import initialize_scheduler, shutdown_scheduler, start_scheduler
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("AI Attendance System Backend starting")
    logger.info(f"🔍 Database connection config - Host: '{settings.DB_HOST}', User: '{settings.DB_USER}', Password length: {len(settings.DB_PASSWORD)}")

    if test_db_connection():
        logger.info("Database connection: OK")
        from app.database.connection import init_db

        try:
            init_db()
        except Exception as exc:
            logger.error("Table initialization failed: %s", str(exc))
    else:
        logger.error("Database connection failed - tables not initialized")

    # Phase 7 Step 1-2: scheduler lifecycle integration
    try:
        initialize_scheduler()
        start_scheduler()
    except Exception as exc:
        # Scheduler failures should not crash API startup.
        logger.exception("event=scheduler_startup_failed message=%s", str(exc))

    yield

    # Shutdown
    try:
        shutdown_scheduler()
    except Exception as exc:
        logger.exception("event=scheduler_shutdown_failed message=%s", str(exc))
    logger.info("Backend shutting down")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="AI Attendance System API",
        description="Backend API for AI-Based Smart Attendance Management System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        debug=settings.DEBUG_MODE,
        lifespan=lifespan,
    )

    app.middleware("http")(security_hardening_middleware)
    app.middleware("http")(log_requests_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_PREFIX)
    register_error_handlers(app)

    @app.get("/")
    async def root():
        return {
            "system": "AI Attendance System",
            "status": "running",
            "version": "1.0.0",
            "docs": "/docs",
        }

    return app


app = create_app()
