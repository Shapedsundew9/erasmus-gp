"""The Gene Pool Interface Abstract Base Class."""

from abc import abstractmethod

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import Logger, egp_logger
from egpdb.configuration import DatabaseConfig
from egppy.genetic_code.ggc_class_factory import GGCDict
from egppy.populations.configuration import PopulationConfig

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class GPIABC(CommonObjABC):
    """Gene Pool Interface Abstract Base Class.

    A Gene Pool Interface is used to interact with the Gene Pool.
    It takes a configuration file describing the Gene Pool database connection
    and provides methods to pull and push Genetic Codes to and from it.
    """

    @abstractmethod
    def __init__(self, config: DatabaseConfig) -> None:
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
    def __setitem__(self, signature: bytes, value: GGCDict) -> None:
        """Set a Genetic Code by its signature."""
        raise NotImplementedError("GPIABC.__setitem__ must be overridden")

    @abstractmethod
    def initial_generation_query(self, pconfig: PopulationConfig) -> list[bytes]:
        """Query the Gene Pool for the initial generation of this population."""
        raise NotImplementedError("GPIABC.initial_generation_query must be overridden")
