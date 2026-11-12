import structlog
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.dal.database import SessionLocal

logger = structlog.get_logger(__name__)


class DalHealth:
    def is_database_reachable(self) -> bool:
        try:
            with SessionLocal() as session:
                session.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            logger.warning("database_unreachable", exc_info=True)
            return False
