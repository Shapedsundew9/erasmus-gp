"""The Gene Pool Interface Abstract Base Class."""

from abc import abstractmethod

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import Logger, egp_logger
from egpdbmgr.configuration import DBManagerConfig
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.populations.configuration import PopulationConfig

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class GPIABC(CommonObjABC):
    """Gene Pool Interface Abstract Base Class.

    A Gene Pool Interface is used to interact with the Gene Pool.
    It takes a DB Manager configuration for the Gene Pool storage role
    and provides methods to pull and push Genetic Codes to and from it.
    """

    @abstractmethod
    def __init__(self, config: DBManagerConfig) -> None:
        """Initialize the Gene Pool Interface."""
        raise NotImplementedError("GPIABC.__init__ must be overridden")

    @abstractmethod
    def __contains__(self, item: bytes) -> bool:
        """Check if a Genetic Code exists in the local cache using its signature."""
        raise NotImplementedError("GPIABC.__contains__ must be overridden")

    @abstractmethod
    def __getitem__(self, item: bytes) -> GGCDict:
        """Get a Genetic Code by its signature."""
        raise NotImplementedError("GPIABC.__getitem__ must be overridden")

    @abstractmethod
    def __setitem__(self, signature: bytes, value: GCABC) -> None:
        """Set a Genetic Code by its signature."""
        raise NotImplementedError("GPIABC.__setitem__ must be overridden")

    @abstractmethod
    def add(self, value: GCABC) -> GGCDict:
        """Place a genetic code in the cache. NB: It is not persisted to the
        database until the cache is flushed / purged.

        The same behaviour as __setitem__ only there is no need to extract the signature
        and the value is returned from the cache.
        """
        raise NotImplementedError("GPIABC.add must be overridden")

    @abstractmethod
    def initial_generation_query(self, pconfig: PopulationConfig) -> list[bytes]:
        """Query the Gene Pool for the initial generation of this population."""
        raise NotImplementedError("GPIABC.initial_generation_query must be overridden")
