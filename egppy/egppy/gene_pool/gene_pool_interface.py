"""The Gene Pool Interface."""

from collections.abc import Iterable
from os.path import dirname, join
from typing import Any, Literal, Sequence

from egpcommon.common import EGP_DEV_PROFILE, EGP_PROFILE
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.properties import GC_TYPE_MASK, GCType
from egpcommon.security import load_signature_data, load_signed_json_list
from egpdb.table import RowIter
from egpdbmgr.db_manager import DBManager, DBManagerConfig
from egppy.gene_pool.gene_pool_interface_abc import GPIABC
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_dict import NULL_GC, GGCDict
from egppy.genetic_code.gpg_view import GPGCView
from egppy.genetic_code.types_def import TypesDef
from egppy.populations.configuration import PopulationConfig
from egppy.storage.cache.cache import DictCache
from egppy.storage.store.db_table_store import DBTableStore

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Source files
SOURCE_FILES = tuple(
    join(dirname(__file__), "..", "data", filename) for filename in ("codons.json",)
)


class GenePoolInterface(GPIABC):
    """Gene Pool Interface.

    A Gene Pool Interface is used to interact with the Gene Pool.
    It takes a configuration file describing the Gene Pool database connection
    and provides methods to pull and push Genetic Codes to and from it.
    """

    def __init__(self, config: DBManagerConfig, cache_size: int = 2**16) -> None:
        """Initialize the Gene Pool Interface.

        The database manager is only configured once. All subsequent initializations
        will use the already configured instances.
        """
        self._dbm = DBManager(config)
        if self._should_reload_sources():
            _logger.info("Developer mode: Reloading Gene Pool data sources.")
            self._dbm = DBManager(config, delete=True)
        self._local_dbt = DBTableStore(self._dbm.managed_gc_table.raw.config, GPGCView, GGCDict)
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
            for filename in SOURCE_FILES:

                # Load the data into the GGC cache
                for ggc_json in load_signed_json_list(filename):
                    ggc = GGCDict(ggc_json)
                    self._ggc_cache[ggc["signature"]] = ggc

                # Add the source file to the sources table
                data = load_signature_data(filename + ".sig")
                data["source_path"] = filename
                self._dbm.managed_sources_table.insert((data,))

            # Make sure all data is written to the database
            self._ggc_cache.copyback()

    def __contains__(self, signature: bytes) -> bool:
        """Check if a Genetic Code exists in the local cache using its signature."""
        return signature in self._ggc_cache

    def __getitem__(self, gc: bytes | GGCDict) -> GGCDict:
        """Get a Genetic Code by its signature."""
        # TODO: Need to handle the case where the GC is not found in the GP.
        # In that case we fall back to the microbiome GPL (which will fallback
        # to the biome GPL etc.) and we could receive a timeout or rate limit
        # response.
        assert isinstance(gc, (bytes, GGCDict)), "gc must be bytes or GGCDict"
        return self._ggc_cache[gc["signature"] if isinstance(gc, GGCDict) else gc]

    def __setitem__(self, signature: bytes, value: GCABC) -> None:
        """Place a genetic code in the cache. NB: It is not persisted to the
        database until the cache is flushed / purged.
        """
        self._ggc_cache[signature] = value if isinstance(value, GGCDict) else GGCDict(value)

    def _should_reload_sources(self) -> bool:
        """Determine if the Gene Pool sources should be reloaded.

        If we are in developer mode and the data sources are different
        from those in the database, then we need to reload them.

        Returns:
            True if sources should be reloaded, False otherwise.
        """
        num_entries = len(self._dbm.managed_sources_table)
        if EGP_PROFILE == EGP_DEV_PROFILE and num_entries >= len(SOURCE_FILES):
            sources: RowIter = self._dbm.managed_sources_table.select()
            hashes: set[bytes] = {row["file_hash"] for row in sources}
            for filename in SOURCE_FILES:
                data = load_signature_data(filename + ".sig")
                file_hash = data["file_hash"]
                if file_hash not in hashes:
                    return True
                hashes.remove(file_hash)
            return bool(hashes)
        return num_entries < len(SOURCE_FILES)

    def consistency(self) -> None:
        """Check the consistency of the Gene Pool."""
        pass

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
        columns: Iterable[str] | Literal["*"] = "*",
    ) -> tuple[dict[str, Any], ...]:
        """Select Genetic Codes based on a SQL query.

        The format of the arguments is for the underlying egpdb.Table.select()

        Args:
            filter_sql: The SQL filter string (without the WHERE).
            order_sql: The SQL order string (without the ORDER BY).
            limit: The maximum number of results to return.
            literals: The literals to use in the SQL query.
        """
        query_str = f" WHERE {filter_sql} ORDER BY {order_sql} LIMIT {max(1, min(limit, 16))}"
        row_iter = self._dbm.managed_gc_table.select(
            query_str, literals, columns=columns, container="dict"
        )
        return tuple(row_iter)

    def select_gc(
        self, where: str, order_by: str, literals: dict[str, Any] | None = None
    ) -> GGCDict:
        """Select a single Genetic Code based on PSQL fragments.

        Args:
            where: The PSQL WHERE fragment (stringized)
            order_by: The PSQL ORDER BY fragment (stringized)

        Returns:
            The selected Genetic Code.
        """
        row_iter = self._dbm.managed_gc_table.select(
            f" WHERE {where} {order_by} LIMIT 1", literals=literals, columns="*", container="dict"
        )
        for ggc in row_iter:
            return GGCDict(ggc)
        raise KeyError("No Genetic Code found matching the query.")

    def verify(self) -> None:
        """Verify the Gene Pool."""
        pass
