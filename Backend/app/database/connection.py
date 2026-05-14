from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import logging

logger = logging.getLogger("ai_attendance")

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    echo=settings.DEBUG_MODE
)

# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create the base class for models
Base = declarative_base()

def get_db():
    """
    Dependency that provides a database session to routes.
    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initializes the database by creating all tables defined in models.
    """
    try:
        from app.models import Base as ModelsBase
        ModelsBase.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database tables: {str(e)}")
        raise e

def test_db_connection():
    """
    Utility to test if the database is reachable.
    Used during server startup.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        # Future: logger.error(f"Database connection failed: {e}")
        print(f"❌ Database connection failed: {e}")
        return False
