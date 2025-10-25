"""EGP Database Manager.

This module provides the database manager for a EGP database.
The EGP database in question may be for the gene-pool or a genomic-library.
There can only be one DB manager for a database at a time.

The DB Manager is responsible for:
    # Creation of the DB as necessary
    # Creation of tables as necessary
    # Initial population of tables (codons etc.)
    # DB data analytics (profiling data, etc.)
    # DB analytics (connection, query, etc.) logging
    # DB maintenance (e.g. vacuuming, re-indexing etc.)
    # Sync'ing the DB back to higher layer databases (micro-biome --> biome etc.)
    # Pulling data from higher layer databases (biome --> micro-biome etc.)
    # DB backup and restore
    # DB migration (e.g. from one version to another)
"""

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any, Callable

from egpcommon.common import SHAPEDSUNDEW9_UUID
from egpcommon.conversions import (
    compress_json,
    decode_properties,
    decompress_json,
    encode_properties,
    memoryview_to_signature,
    signature_to_bytes,
)
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.gp_db_config import GGC_KVT
from egpdb.raw_table import ColumnSchema
from egpdb.table import Table, TableConfig
from egpdbmgr.configuration import DBManagerConfig, TableTypes

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Note that encode conversions must produce a type that is compatible with the database type
# and decode conversions must produce a type that is compatible with the application type.
# The conversions *MUST* be symmetric i.e. encode followed by decode must produce the original
# value.
# {name, encode (output to DB), decode (output to application)}
GC_TABLE_CONVERSIONS: tuple[tuple[str, Callable | None, Callable | None], ...] = (
    (
        "cgraph",
        lambda x: compress_json(x.to_json(True)),
        decompress_json,
    ),
    ("meta_data", compress_json, decompress_json),
    ("properties", encode_properties, decode_properties),
) + tuple(
    (name, signature_to_bytes, memoryview_to_signature)
    for name, field in GGC_KVT.items()
    if field.get("phy_type", "").endswith("Sig")
)
META_TABLE_SCHEMA: dict[str, dict[str, Any]] = {
    "created": {"db_type": "TIMESTAMP", "nullable": False},
    "creator": {"db_type": "UUID", "nullable": False},
}
SOURCES_TABLE_SCHEMA: dict[str, ColumnSchema] = {
    "source_path": ColumnSchema(db_type="VARCHAR", nullable=False),
    "creator_uuid": ColumnSchema(db_type="VARCHAR", nullable=False),
    "timestamp": ColumnSchema(db_type="VARCHAR", nullable=False),
    "file_hash": ColumnSchema(db_type="VARCHAR", nullable=False),
    "signature": ColumnSchema(db_type="VARCHAR", nullable=False),
    "algorithm": ColumnSchema(db_type="VARCHAR", nullable=False),
}


class DBManager:
    """Database Manager for the EGP."""

    def __init__(self, config: DBManagerConfig, delete: bool = False) -> None:
        self.config = config
        self._delete = delete  # Delete existing tables if True
        self.managed_gc_table = self.create_managed_table()
        self.managed_gc_meta_table = self.create_managed_meta_table()
        self.managed_sources_table = self.create_managed_sources_table()

        if self.managed_gc_meta_table.raw.creator:
            self.managed_gc_meta_table.insert(
                # TODO: Need to get the creator from the commandline or config
                (
                    {
                        "creator": str(SHAPEDSUNDEW9_UUID),
                        "created": datetime.now(UTC).isoformat(),
                    },
                )
            )

    def prepare_schemas(self) -> dict[TableTypes, dict[str, Any]]:
        """Prepare the schemas for the different table types.
        The GenePool schema is defined by default in gp_db_config.py
        and the other schemas are variants on that.
        """
        schema = {k: v for k, v in GGC_KVT.items() if v}
        schemas = {k: deepcopy(schema) for k in TableTypes}
        # TODO: Optimise other schemas
        return schemas

    def create_managed_table(self) -> Table:
        """Create and return the managed Table object for the DB Manager."""
        schemas = self.prepare_schemas()
        schema = schemas[self.config.managed_type]
        # Check if remote DB exists. If so download from there.
        # If not download database file from remote URL: Check if it is signed.
        table_config = TableConfig(
            database=self.config.databases[self.config.managed_db],
            table=self.config.managed_type + "_table",
            schema={
                # Filter out non-ColumnSchema parameters
                k1: {k2: v2 for k2, v2 in v1.items() if k2 in ColumnSchema.parameters}
                for k1, v1 in schema.items()
            },
            create_db=True,
            create_table=True,
            delete_table=self._delete,
            conversions=GC_TABLE_CONVERSIONS,
        )
        return Table(table_config)

    def create_managed_meta_table(self) -> Table:
        """Create and return the managed meta Table object for the DB Manager."""
        # Check if remote DB exists. If so download from there.
        # If not download database file from remote URL: Check if it is signed.
        table_config = TableConfig(
            database=self.config.databases[self.config.managed_db],
            table=self.config.managed_type + "_meta_table",
            schema=META_TABLE_SCHEMA,
            create_db=True,
            create_table=True,
            delete_table=self._delete,
        )
        return Table(table_config)

    def create_managed_sources_table(self) -> Table:
        """Create and return the managed sources Table object for the DB Manager."""
        # Check if remote DB exists. If so download from there.
        # If not download database file from remote URL: Check if it is signed.
        table_config = TableConfig(
            database=self.config.databases[self.config.managed_db],
            table=self.config.managed_type + "_sources_table",
            schema=SOURCES_TABLE_SCHEMA,
            create_db=True,
            create_table=True,
            delete_table=self._delete,
        )
        return Table(table_config)

    def operations(self) -> None:
        """Operations for the DB Manager."""
        _logger.info("Operations for the DB Manager for config named '%s'.", self.config.name)
