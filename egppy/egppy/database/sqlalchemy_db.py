"""SQLAlchemy database interface implementation module."""
from logging import Logger, NullHandler, getLogger, DEBUG
from sqlalchemy import create_engine
from egppy.database.db_abc import DBABC


# Standard EGP logging pattern
_logger: Logger = getLogger(__name__)
_logger.addHandler(NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(DEBUG)


def maintenance_uri_end(db_config: dict[str, any], password: str) -> str:
    """
    Get the maintenance URI for the database.

    Args:
        db_config: The configuration of the database.
        password: The password for the database user.

    Returns:
        The maintenance URI for the database.
    """
    user = db_config.get("maintenance_user", "postgres")
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    dbname = db_config.get("maintenance_db", "postgres")
    return f"://{user}:{password}@{host}:{port}/{dbname}"


class SQLAlchemySqliteMem(DBABC):
    """SQLAlchemy database interface implementation for an in-memory SQLite database."""

    def __init__(self, db_config: dict[str, any]) -> None:
        """
        Initialize the database.
        If the database does not exist, create it.

        Args:
            db_name: The name of the database.
        """
        super().__init__(db_config)
        self.engine = create_engine("sqlite://")
        self.conn = self.engine.connect()

    def exists(self) -> bool:
        """Check if the database exists."""
        return True
