from sqlalchemy.orm import Session
import logging

logger = logging.getLogger("ai_attendance")

def db_transaction(db: Session, operation_name: str = "DB Operation"):
    """
    A utility to handle database commits and rollbacks safely.
    Use this when performing writes (Create, Update, Delete).
    """
    try:
        db.commit()
        logger.debug(f"✅ {operation_name} successful")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"❌ {operation_name} failed: {str(e)}")
        return False

def validate_schema_integrity(db: Session):
    """
    Basic utility to check if core tables are accessible.
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.get_bind())
        tables = inspector.get_table_names()
        required_tables = ["students", "attendance", "admins"]
        
        missing = [t for t in required_tables if t not in tables]
        if missing:
            logger.warning(f"⚠️ Missing tables: {', '.join(missing)}")
            return False
        return True
    except Exception as e:
        logger.error(f"❌ Schema validation error: {str(e)}")
        return False
