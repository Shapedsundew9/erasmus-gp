"""Types Definition Database.

The TDDB is a double dictionary that maps type names to TypesDef objects
and type UIDs to TypesDef objects. It is implemented as a cache of the
full types database which is a local postgres database.

The expectation is that the types used at runtime will be small enough
to fit in memory (but the user should look for frequent cache evictions
in the logs and adjust the cache size accordingly) as EGP should use a tight
subset for a population.

New compund types can be created during evolution requiring the  cache and
datbase to be updated. Since types have to be globally unique a cloud service
call is required to create a new type.

Initialization follow the following steps:
    1. Load the pre-defined types from the local JSON file.
    2. Generate the abstract type fixed versions.
    3. Generate the output wildcard meta-types.
    4. Push the types to the database.
    5. Initialise the empty cache.
"""

from __future__ import annotations

from json import dumps, loads
from os.path import dirname, join
from weakref import WeakValueDictionary

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging
from egpcommon.common import EGP_PROFILE, EGP_DEV_PROFILE
from egpdb.configuration import ColumnSchema
from egpdb.table import Table, TableConfig

from egppy.c_graph.end_point.types_def.types_def import TypesDef
from egppy.local_db_config import LOCAL_DB_CONFIG

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)
enable_debug_logging()

# Initialize the database connection
NAME_TO_TD_MAP: WeakValueDictionary[str, TypesDef] = WeakValueDictionary()
UID_TO_TD_MAP: WeakValueDictionary[int, TypesDef] = WeakValueDictionary()
DB_STORE = Table(
    config=TableConfig(
        database=LOCAL_DB_CONFIG,
        table="types_def",
        schema={
            "uid": ColumnSchema(db_type="int4", primary_key=True),
            "name": ColumnSchema(db_type="VARCHAR", index="btree"),
            "default": ColumnSchema(db_type="VARCHAR", nullable=True),
            "abstract": ColumnSchema(db_type="bool"),
            "ept": ColumnSchema(db_type="INT4[]"),
            "imports": ColumnSchema(db_type="VARCHAR"),
            "parents": ColumnSchema(db_type="VARCHAR"),
            "children": ColumnSchema(db_type="VARCHAR"),
        },
        data_file_folder=join(dirname(__file__), "..", "..", "..", "data"),
        data_files=["types_def.json"],
        delete_table=EGP_PROFILE == EGP_DEV_PROFILE,
        create_db=True,
        create_table=True,
        conversions=(
            ("imports", dumps, loads),
            ("parents", dumps, loads),
            ("children", dumps, loads),
        ),
    ),
)


def types_def_db(identifier: int | str) -> TypesDef:
    """Return the TypesDef object for the given identifier.

    Args:
        identifier (int | str): Either the UID or name of the type.

    Returns:
        TypesDef: The TypesDef object for the given identifier.
    """
    if isinstance(identifier, int):
        if identifier in UID_TO_TD_MAP:
            return UID_TO_TD_MAP[identifier]
        td = DB_STORE.get(identifier, {})
    elif isinstance(identifier, str):
        if identifier in NAME_TO_TD_MAP:
            return NAME_TO_TD_MAP[identifier]
        tds = tuple(DB_STORE.select("WHERE name = {id}", literals={"id": identifier}))
        td = tds[0] if len(tds) == 1 else {}
    else:
        raise ValueError(f"Invalid identifier type: {type(identifier)}")

    if not td:
        # Type definition is not in the local database
        # TODO: Call out to the global service to get the type definition
        raise ValueError(f"Type definition not found for identifier: {identifier}")

    # Create the TypesDef object
    ntd = TypesDef(**td)
    NAME_TO_TD_MAP[ntd.name] = ntd
    UID_TO_TD_MAP[ntd.uid] = ntd
    return ntd


# Important check
assert types_def_db("tuple").uid == 200, "Tuple UID is used as a constant in types_def.py"
