"""The Gene Pool Interface."""

from os.path import dirname, join

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.security import load_signed_json_list
from egpdb.configuration import ColumnSchema, DatabaseConfig, TableConfig
from egppy.gene_pool.gene_pool_interface_abc import GPIABC
from egppy.genetic_code.ggc_class_factory import GGCDict
from egppy.genetic_code.interface import Interface
from egppy.local_db_config import LOCAL_DB_CONFIG
from egppy.populations.configuration import PopulationConfig
from egppy.storage.cache.cache import DictCache
from egppy.storage.store.db_table_store import DBTableStore

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Initialize the local database connection
# The local database is more highly indexed than the Gene Pool
# but contains the same data.
DB_TABLE_CONFIG = TableConfig(
    database=LOCAL_DB_CONFIG,
    table="local_gc_store",
    schema={
        k: ColumnSchema(**{k1: v1 for k1, v1 in v.items() if k1 in ColumnSchema.parameters})
        for k, v in GGCDict.GC_KEY_TYPES.items()
        if v
    },
    delete_table=False,
    create_db=True,
    create_table=True,
    conversions=GGCDict.CONVERSIONS,
)

_LOCAL_DB_STORE = DBTableStore(DB_TABLE_CONFIG, GGCDict)
GGC_CACHE = DictCache(
    {"max_items": 2**16, "purge_count": 2**14, "flavor": GGCDict, "next_level": _LOCAL_DB_STORE}
)


class GenePoolInterface(GPIABC):
    """Gene Pool Interface.

    A Gene Pool Interface is used to interact with the Gene Pool.
    It takes a configuration file describing the Gene Pool database connection
    and provides methods to pull and push Genetic Codes to and from it.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """Initialize the Gene Pool Interface."""
        self.config = config.copy()

    def _populate_locally(self):
        """Populate Gene Pool from the local datafiles."""
        data_file_folder = (dirname(__file__), "..", "..", "..", "egpdbmgr", "egpdbmgr", "data")
        for data_file in ["meta_codons.json", "codons.json"]:
            for gc in load_signed_json_list(join(*data_file_folder, data_file)):
                ggc = GGCDict(gc)
                if ggc["signature"] not in GGC_CACHE:
                    GGC_CACHE[ggc["signature"]] = ggc
        GGC_CACHE.copyback()

    def consistency(self) -> bool:
        """Check the consistency of the Gene Pool."""
        return True

    def initial_generation_query(self, pconfig: PopulationConfig) -> list[bytes]:
        """Query the Gene Pool for the initial generation of this population."""
        # Place holder for the actual implementation
        return []

    def select_gc(self, _: Interface) -> bytes | None:
        """Select a Genetic Code with the exact input types."""
        # Place holder for the actual implementation
        return None

    def verify(self) -> bool:
        """Verify the Gene Pool."""
        return True
