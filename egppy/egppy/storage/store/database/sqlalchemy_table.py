"""SQLAlchemy table class implamentation module."""
from sqlalchemy.sql import text
from egppy.database.table_abc import TableABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class SQLAlchemyTable(TableABC):
    """SQLAlchemy table class implementation module."""

    def __contains__(self, pk_value: any) -> bool:
        """
        Check if a primary key value exists in the table.

        Args:
            pk_value: The primary key value.

        Returns:
            True if a primary key with the value exists, False otherwise.
            If the table does not have a primary key, return False.
        """

    def __delitem__(self, pk_value: any) -> None:
        """
        Delete a row from the table by primary key.
        If the primary key value does not exist, raise a KeyError.
        If the table does not have a primary key, raise a KeyError.

        Args:
            pk_value: The primary key value.
        """

    def __getitem__(self, pk_value: any) -> dict[str, any]:
        """
        Get a row from the table by primary key.

        Args:
            pk_value: The primary key value.

        Returns:
            The row with the primary key value as a dict of column names to values.
            If the table does not have a primary key or the primary key value does not exist
            a KeyError is raised.
        """

    def __len__(self) -> int:
        """
        Get the number of rows in the table.

        Returns:
            The number of rows in the table.
        """

    def __setitem__(self, pk_value: any, row: dict[str, any]) -> None:
        """
        Set a row in the table by primary key.

        Args:
            pk_value: The primary key value.
            row: The row as a dict of column names to values.
        """

    def _column_create_sql(self) -> tuple[str, dict[str, any]]:
        """
        Get the SQL to create a column.

        Args:
            column: The column schema.

        Returns:
            The SQL to create the column with bounded parameters.
        """
        literals = {}
        sql_str = ""
        for name, definition in self._config["schema"].items():
            sql_str += name + " " + definition["type"]
            if not definition.get("nullable", True):
                sql_str += " NOT NULL"
            if definition.get("primary_key", False):
                sql_str += " PRIMARY KEY"
            if definition.get("unique", False) and not definition.get("primary_key", False):
                sql_str += " UNIQUE"
            if "default" in definition:
                sql_str += " DEFAULT :" + name
                literals[name] = definition["default"]
        return sql_str, literals

    def create(self) -> None:
        """Create the table."""
        column_sql, literals = self._column_create_sql()
        query = text(f"CREATE TABLE {self._config['table']} ({column_sql})")
        self._database.conn.execute(query, literals)

    def delete(self, sqltoken: str) -> None:
        return super().delete(sqltoken)

    def drop(self) -> None:
        """Drop the table."""
        query = text(f"DROP TABLE {self._config['table']}")
        self._database.conn.execute(query)

    def exists(self) -> bool:
        """Check if the table exists."""
        query = text("SELECT name FROM sqlite_master WHERE type=:type AND name=:table")
        literals = {"type": "table", "table": self._config["table"]}
        result = self._database.conn.execute(query, literals).scalar()
        return result is not None

    def select(self, sqltoken: str) -> tuple[tuple, ...]:
        return super().select(sqltoken)

    def upsert(self, sqltoken: str, data: tuple[tuple | list, ...]) -> None:
        return super().upsert(sqltoken, data)

    def wait(self) -> None:
        return super().wait()
