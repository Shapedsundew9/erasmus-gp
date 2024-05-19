"""Abstract base class for database tables."""
from abc import ABC, abstractmethod
from egppy.database.db_abc import DBABC


# Mapping of types to byte alignments (postgresql)
TYPE_ALIGNMENTS: dict[str, int] = {
    "BIGINT": 8,
    "BOOL": 1,
    "BOOLEAN": 1,
    "DOUBLE PRECISION": 8,
    "INTEGER": 4,
    "INT4": 4,
    "INT": 4,
    "INTERVAL": 8,
    "REAL": 4,
    "FLOAT4": 4,
    "SMALLINT": 2,
    "INT2": 2,
    "SERIAL4": 4,
    "TIMESTAMP": 8,
    "UUID": 8
}


class TableABC(ABC):
    """Abstract base class for database tables."""

    @abstractmethod
    def __init__(self, table_schema: dict[str, any], database: DBABC) -> None:
        """
        Initialize the table.
        If the table does not exist, create it.

        Args:
            table_schema: The schema of the table.
        """
        self._database: DBABC = database
        self._config: dict[str, any] = table_schema
        self._add_alignment()
        self._table_existence()

    @abstractmethod
    def __contains__(self, pk_value: any) -> bool:
        """
        Check if a primary key value exists in the table.

        Args:
            pk_value: The primary key value.

        Returns:
            True if a primary key with the value exists, False otherwise.
            If the table does not have a primary key, return False.
        """

    @abstractmethod
    def __delitem__(self, pk_value: any) -> None:
        """
        Delete a row from the table by primary key.
        If the primary key value does not exist, raise a KeyError.
        If the table does not have a primary key, raise a KeyError.

        Args:
            pk_value: The primary key value.
        """

    @abstractmethod
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

    @abstractmethod
    def __len__(self) -> int:
        """
        Get the number of rows in the table.

        Returns:
            The number of rows in the table.
        """

    @abstractmethod
    def __setitem__(self, pk_value: any, data: dict[str, any]) -> None:
        """
        Set a row in the table by primary key.
        If the primary key value does not exist, insert a new row.
        If the primary key value exists, update the row.
        If the table does not have a primary key, raise a KeyError.
        If a column is not set that does not have a default value, raise a ValueError.

        Args:
            pk_value: The primary key value.
            data: The row to set.
        """

    def _add_alignment(self):
        """Add the byte alignment of the column type to the column definition in self._config

        Alignment depends on the column type and is an integer number of bytes usually
        1, 2, 4 or 8. A value of 0 is used to define a variable alignment field.
        """
        for definition in self._config["schema"].values():
            definition["alignment"] = TYPE_ALIGNMENTS.get(definition["type"], 0)

    def _table_existence(self) -> None:
        """
        Logic to delete, wait or create a table.
        """
        if self._config.get("delete", False):
            self.drop()
        if self._config.get("wait", False):
            self.wait()
        elif self._config.get("create", True):
            self.create()
        assert self.exists(), "Table does not exist and there is no path to existance."

    @abstractmethod
    def create(self) -> None:
        """
        Create the table.
        """

    @abstractmethod
    def delete(self, sqltoken: str) -> None:
        """
        Delete rows from the table.

        Args:
            where: The selection criteria.
        """

    @abstractmethod
    def drop(self) -> None:
        """
        Drop the table.
        """

    @abstractmethod
    def exists(self) -> bool:
        """
        Check if the table exists.

        Returns:
            True if the table exists, False otherwise.
        """

    @abstractmethod
    def select(self, sqltoken: str) -> tuple[tuple, ...]:
        """
        Select rows from the table using the implementation's SQL dialect defined
        by the token.

        Args:
            where: The selection criteria.

        Returns:
            A tuple of the selected row values in a tuple.
        """

    @abstractmethod
    def upsert(self, sqltoken: str, data: tuple[tuple | list, ...]) -> None:
        """
        Update or insert a row into the table.

        Args:
            data: The row to insert.
        """

    @abstractmethod
    def wait(self) -> None:
        """
        Wait for the table to exist.
        """
