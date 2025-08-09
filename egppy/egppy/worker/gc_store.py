"""Genetic Code store for the worker object."""

from os.path import dirname, join

from egpcommon.common import EGP_DEV_PROFILE, EGP_PROFILE
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.security import load_signed_json_list
from egpdb.configuration import ColumnSchema, TableConfig
from egppy.genetic_code.ggc_class_factory import GGCDict
from egppy.local_db_config import LOCAL_DB_CONFIG
from egppy.storage.cache.cache import DictCache
from egppy.storage.store.db_table_store import DBTableStore

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Initialize the database connection
DB_TABLE_CONFIG = TableConfig(
    database=LOCAL_DB_CONFIG,
    table="local_gc_store",
    schema={k: ColumnSchema(**v) for k, v in GGCDict.GC_KEY_TYPES.items() if v},  # type: ignore
    delete_table=False,  # EGP_PROFILE == EGP_DEV_PROFILE,
    create_db=True,
    create_table=True,
    conversions=GGCDict.CONVERSIONS,
)

_LOCAL_DB_STORE = DBTableStore(DB_TABLE_CONFIG, GGCDict)
GGC_CACHE = DictCache(
    {"max_items": 2**20, "purge_count": 2**18, "flavor": GGCDict, "next_level": _LOCAL_DB_STORE}
)

data_file_folder = (dirname(__file__), "..", "..", "..", "egpdbmgr", "egpdbmgr", "data")
for data_file in ["meta_codons.json", "codons.json"]:
    for gc in load_signed_json_list(join(*data_file_folder, data_file)):
        ggc = GGCDict(gc)
        if ggc["signature"] not in GGC_CACHE:
            GGC_CACHE[ggc["signature"]] = ggc
GGC_CACHE.copyback()
