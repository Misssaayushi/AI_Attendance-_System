from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings
import logging

logger = logging.getLogger("ai_attendance")

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
    pool_timeout=settings.DB_POOL_TIMEOUT_SECONDS,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
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
    Initializes the database by creating all tables defined in models
    and seeds a default admin user if none exists.
    """
    try:
        from app.models import Base as ModelsBase
        ModelsBase.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized successfully")
        
        # Seed default admin if table is empty
        from app.models.admin import Admin
        from app.utils.security import get_password_hash
        
        db = SessionLocal()
        try:
            admin_user = db.query(Admin).filter_by(username="admin").first()
            if not admin_user:
                default_admin = Admin(
                    username="admin",
                    password=get_password_hash("admin123")
                )
                db.add(default_admin)
                db.commit()
                logger.info("👤 Default admin user seeded successfully (username: admin, password: admin123)")
            else:
                admin_user.password = get_password_hash("admin123")
                db.commit()
                logger.info("👤 Existing 'admin' user password reset to 'admin123'")
        except Exception as se:
            logger.error(f"⚠️ Failed to seed default admin: {se}")
            db.rollback()
        finally:
            db.close()
            
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
