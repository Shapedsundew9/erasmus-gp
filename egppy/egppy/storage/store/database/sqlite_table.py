"""SQLAlchemy table class implamentation module."""
from copy import deepcopy
from egppy.database.sqlalchemy_db import SQLAlchemySqliteMem
from egppy.database.sqlalchemy_table import SQLAlchemyTable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Mapping of types from the table schema to sqlite3 types.
MAP_TYPE = {
    "UUID": "BLOB",
    "BYTEA": "BLOB"
}


def map_config(table_schema: dict[str, any]) -> dict[str, any]:
    """
    Map the table schema types to sqlite compatible ones.

    Args:
        table_schema: The schema of the table.

    Returns:
        The configuration for creating the table.
    """
    config = deepcopy(table_schema)
    for column in config["schema"].values():
        column["type"] = MAP_TYPE.get(column["type"], column["type"])
    return config


class SQLiteTable(SQLAlchemyTable):
    """SQLAlchemy table class implementation module."""

    def __init__(self, table_schema: dict[str, any], database: SQLAlchemySqliteMem) -> None:
        """
        Initialize the table.
        If the table does not exist, create it.

        Args:
            table_schema: The schema of the table.
        """
        super().__init__(map_config(table_schema), database)
        self._base_config = deepcopy(table_schema)
