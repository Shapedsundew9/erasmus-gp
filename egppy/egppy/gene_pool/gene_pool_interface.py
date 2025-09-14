"""The Gene Pool Interface."""

from os.path import dirname, join
from typing import Any

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.security import load_signed_json_list
from egpdbmgr.db_manager import DBManager, DBManagerConfig
from egppy.gene_pool.gene_pool_interface_abc import GPIABC
from egppy.genetic_code.ggc_class_factory import GGCDict
from egppy.genetic_code.interface import Interface
from egppy.populations.configuration import PopulationConfig
from egppy.storage.cache.cache import DictCache
from egppy.storage.store.db_table_store import DBTableStore

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GenePoolInterface(GPIABC):
    """Gene Pool Interface.

    A Gene Pool Interface is used to interact with the Gene Pool.
    It takes a configuration file describing the Gene Pool database connection
    and provides methods to pull and push Genetic Codes to and from it.
    """

    def __init__(self, config: DBManagerConfig | None = None, cache_size: int = 2**16) -> None:
        """Initialize the Gene Pool Interface.

        The database manager is only configured once. All subsequent initializations
        will use the already configured instances.
        """
        if config is None:
            raise ValueError("A DBManagerConfig must be provided for the first initialization.")
        self._dbm = DBManager(config)
        self._local_dbt = DBTableStore(self._dbm.managed_table.raw.config, GGCDict)
        self._ggc_cache = DictCache(
            {
                "max_items": cache_size,
                "purge_count": cache_size // 4,
                "flavor": GGCDict,
                "next_level": self._local_dbt,
            }
        )

        # If the database is empty, we need to populate it with the initial codes
        # based on the configuration.
        # TODO: Make this controllable via the configuration.
        if not self._local_dbt:
            for filename in ("codons.json", "meta_codons.json"):
                for ggc_json in load_signed_json_list(
                    join(dirname(__file__), "..", "data", filename)
                ):
                    ggc = GGCDict(ggc_json)
                    self._ggc_cache[ggc["signature"]] = ggc
            self._ggc_cache.copyback()
        self._initialization_complete = True

    def __getitem__(self, signature: bytes) -> GGCDict:
        """Get a Genetic Code by its signature."""
        return self._ggc_cache[signature]

    def __setitem__(self, signature: bytes, value: GGCDict) -> None:
        """Set a Genetic Code by its signature."""
        self._ggc_cache[signature] = value

    def consistency(self) -> bool:
        """Check the consistency of the Gene Pool."""
        return True

    def initial_generation_query(self, pconfig: PopulationConfig) -> list[bytes]:
        """Query the Gene Pool for the initial generation of this population."""
        # Place holder for the actual implementation
        return []

    def select(
        self,
        filter_sql: str,
        order_sql: str = "RANDOM()",
        limit: int = 1,
        literals: dict[str, Any] | None = None,
    ) -> tuple[bytes, ...]:
        """Select Genetic Codes based on a SQL query.

        The format of the arguments is for the underlying egpdb.Table.select()

        Args:
            filter_sql: The SQL filter string (without the WHERE).
            order_sql: The SQL order string (without the ORDER BY).
            limit: The maximum number of results to return.
            literals: The literals to use in the SQL query.
        """
        query_str = f" WHERE {filter_sql} ORDER BY {order_sql} LIMIT {max(1, min(limit, 16))}"
        row_iter = self._dbm.managed_table.select(
            query_str, literals, columns=["signature"], container="tuple"
        )
        return tuple(row[0] for row in row_iter)

    def select_interface(self, _: Interface) -> bytes | None:
        """Select a Genetic Code with the exact input types."""
        # Place holder for the actual implementation
        return None

    def verify(self) -> bool:
        """Verify the Gene Pool."""
        return True
