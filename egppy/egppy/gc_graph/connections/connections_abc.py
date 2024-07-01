"""Connections Abstract Base Class"""
from typing import Any
from abc import ABC, abstractmethod
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ConnectionsABC(ABC):
    """Abstract Base Class for Genetic Code Graph Connections between Interface Endpoints.

    ConnectionsABC does not inherent from CacheableObjABC because the connections are
    stored within the graph object and are not cached separately.

    Connections are read-only once created. Modifying connections (and interfaces) is
    done by manipluating endpoints which are written to the read-only connections object
    when complete.

    Connections can be considered as a tuple-like of tuple-likes of endpoint references.
    Even if an endpoint has no connections it must be represented by an empty tuple-like.
    If an interface has no endpoints it must be represented by an empty tuple-like.
    Consequently the length of an interface is the same as the length of the connections.

    In theory connection objects can be shared between multiple graphs.
    """

    @abstractmethod
    def __getitem__(self, index: int) -> Any:
        """Return the list of connections."""
        raise NotImplementedError("Connections.__getitem__ must be overridden")

    @abstractmethod
    def __iter__(self) -> Any:
        """Iterate over the connections."""
        raise NotImplementedError("Connections.__iter__ must be overridden")

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of endpoints (connections).
        NOTE: An endpoint may have no connections but still be valid.
        """
        raise NotImplementedError("Connections.__len__ must be overridden")

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the Connections.
        The consistency() method is used to check the consistency of the Connections
        object. This method is called by the copyback() method to ensure that
        the object is in a consistent state before it is copied back if the
        log level is set to CONSISTENCY. The
        consistency() method should raise an exception if the object is not
        consistent. The consistency() method may also be called by the user
        to check the consistency of the object.
        NOTE: Likely to significantly slow down the code.
        """
        raise NotImplementedError("Connections.consistency must be overridden")

    @abstractmethod
    def verify(self) -> None:
        """Verify the Connections object.
        The verify() method is used to check the Connections object for validity.
        The verify() method should raise an exception if the object is not
        valid. The verify() method may also be called by the user to check the
        validity of the object. The verify() method is called by the copyback()
        method if the _LOG_VERIFY level is set. The verify() method should not
        be called by the user unless the user has a good reason to do so.
        NOTE: May significantly slow down the code if called frequently.
        """
        raise NotImplementedError("Connections.verify must be overridden")
