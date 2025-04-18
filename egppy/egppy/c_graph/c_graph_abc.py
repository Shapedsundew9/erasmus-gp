"""Abstract base class for Connection Graph objects."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.properties import CGraphType

from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CGraphABC(CacheableObjABC):
    """Abstract Base Class for Genetic Code Graphs.

    The graph abstract base class, CGraphABC, is the base class for all genetic code graph objects.
    Connection Graph objects define connections between interfaces.

    A row is a tuple of interfaces. The row is keyed by a capital letter (used for __contains__)
        e.g. 'A', 'B', 'I', 'O' etc.
    An interface is keyed by the row letter and 's' or 'd' for source or destination.
        e.g. 'As', 'Bd', 'Is', 'Od' etc.
    An interfaces connections uses the interface key with a 'c' appended:
        e.g. 'Asc', 'Bdc', 'Isc', 'Odc' etc.
    Endpoints are keyed by the row letter, a 3 digit index and 's' or 'd'.
        e.g. 'A000s', 'B002d', 'I013s', 'O255d' etc.

    The keys above can be used with:
        __contains__    (required by CacheableObjABC. Mixed in)
        __hash__      (required by CacheableObjABC. Mixed in)
        __iter__       (required by CacheableObjABC. Mixed in)
        __len__        (required by CacheableObjABC. Mixed in)
        __delitem__
        __getitem__
        __setitem__
        get             (mixed in)
        setdefault      (mixed in)

    In addition the following methods are required by CacheableObjABC:
        __iter__ must iterate through the endpoints (mixed in)
        __len__ must return the total number of endpoints.
        __contains__ must return True if the endpoint exists. (mixed in)

    Appending and deleting endpoints is done by replacing the 3 digit index with +++ or ---.
        e.g. 'A+++s', 'B---d', 'I+++s', 'O---d' etc.
    """

    @abstractmethod
    def __contains__(self, key: object) -> bool:
        """Return True if the endpoint exists."""
        raise NotImplementedError("CGraphABC.__contains__ must be overridden")

    @abstractmethod
    def __delitem__(self, key: str) -> None:
        """Delete the endpoint with the given key."""
        raise NotImplementedError("CGraphABC.__delitem__ must be overridden")

    @abstractmethod
    def __getitem__(self, key: str) -> Any:
        """Get the endpoint with the given key."""
        raise NotImplementedError("CGraphABC.__getitem__ must be overridden")

    @abstractmethod
    def __setitem__(self, key: str, value: Any) -> None:
        """Set the endpoint with the given key."""
        raise NotImplementedError("CGraphABC.__setitem__ must be overridden")

    @abstractmethod
    def type(self) -> CGraphType:
        """Return the type of the graph."""
        raise NotImplementedError("CGraphABC.type must be overridden")

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Get the endpoint with the given key or return the default."""
        raise NotImplementedError("CGraphABC.get must be overridden")

    @abstractmethod
    def is_stable(self) -> bool:
        """Return True if the graph is stable."""
        raise NotImplementedError("CGraphABC.is_stable must be overridden")

    @abstractmethod
    def stabilize(self, fixed_interface: bool = True):
        """Stabilize the genetic code object."""
        raise NotImplementedError("GCABC.stabilize must be overridden")
