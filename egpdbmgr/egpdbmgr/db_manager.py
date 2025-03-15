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
from os.path import dirname, join

from egpcommon.common import GGC_KVT
from egpcommon.properties import PropertiesBD
from egpcommon.conversions import (
    compress_json,
    decompress_json,
    list_int_to_bytes,
)
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpdb.database import db_exists
from egpdb.table import Table, TableConfig

from egpdbmgr.configuration import TABLE_TYPES, DBManagerConfig

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Constants
GP_SCHEMA = deepcopy(GGC_KVT)
GP_SCHEMA["signature"] = GP_SCHEMA["signature"] | {"primary_key": True}
SCHEMAS = {"pool": GP_SCHEMA, "library": GP_SCHEMA, "archive": GGC_KVT}
assert set(SCHEMAS.keys()) == set(TABLE_TYPES)


def encode_properties(properties: dict) -> int:
    """Encode properties."""
    return PropertiesBD(properties).to_int()


def decode_properties(properties: int) -> dict:
    """Decode properties."""
    return PropertiesBD(properties).to_json()


def initialize(config: DBManagerConfig) -> bool:
    """Initialize the DB Manager.

    Return True if a restart is required.
    """
    if db_exists(config.local_db, config.databases[config.local_db]):
        _logger.info("Database '%s' exists.", config.local_db)
        # Check table version
        # Migrate table if necessary
        # Check table data
        # Spawn processes
    else:
        schema = SCHEMAS[config.local_type]
        # Check if remote DB exists. If so download from there.
        # If not download database file from remote URL: Check if it is signed.
        table_config = TableConfig(
            database=config.databases[config.local_db],
            table=config.local_type + "_table",
            schema=schema,
            create_db=True,
            create_table=True,
            data_file_folder=join(dirname(__file__), "data"),
            data_files=["codons.json"],
            conversions=(
                ("graph", compress_json, decompress_json),
                ("meta_data", compress_json, decompress_json),
                ("properties", encode_properties, decode_properties),
                ("outputs", list_int_to_bytes, None),
                ("inputs", list_int_to_bytes, None),
            ),
        )
        _ = Table(table_config)
        return True
    _logger.info("Initializing the DB Manager for config named '%s'.", config.name)
    return False


def operations(config: DBManagerConfig) -> None:
    """Operations for the DB Manager."""
    _logger.info("Operations for the DB Manager for config named '%s'.", config.name)
