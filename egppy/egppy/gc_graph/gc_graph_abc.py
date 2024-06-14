"""Abstract base class for GC graph objects."""
from __future__ import annotations
from abc import abstractmethod, ABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.interface.interface_abc import InterfaceABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCGraphABC(ABC):
    """Abstract Base Class for Genetic Code Graphs.
    
    The graph abstract base class, GCGraphABC, is the base class for all genetic code graph objects.
    GC graph objects define connections between interfaces.

    Keys accessing items in the graph use the following format:
        [Row][s|d]
    where Row is the capitalized row letter and s|d represents a source or destination
    Every key is therefore exactly 2 characters long. e.g. Ad, Bs, Od etc. 
    """

    @abstractmethod
    def get_interface(self, key: str) -> InterfaceABC:
        """Return the interface object for the given key"""
        raise NotImplementedError("GCGraphABC.get_interface must be overridden")

    @abstractmethod
    def get_connections(self, key: str) -> InterfaceABC:
        """Return the interface object for the given key"""
        raise NotImplementedError("GCGraphABC.get_interface must be overridden")

    @abstractmethod
    def consistency(self) -> None:
        """Check the consistency of the GCGraphABC.
        The consistency() method is used to check the consistency of the GCGraphABC
        object. This method is called by the copyback() method to ensure that
        the object is in a consistent state before it is copied back if the
        log level is set to CONSISTENCY. The
        consistency() method should raise an exception if the object is not
        consistent. The consistency() method may also be called by the user
        to check the consistency of the object.
        NOTE: Likely to significantly slow down the code.
        """
        raise NotImplementedError("GCGraphABC.consistency must be overridden")

    @abstractmethod
    def verify(self) -> None:
        """Verify the GCGraphABC object.
        The verify() method is used to check the GCGraphABC object for validity.
        The verify() method should raise an exception if the object is not
        valid. The verify() method may also be called by the user to check the
        validity of the object. The verify() method is called by the copyback()
        method if the _LOG_VERIFY level is set. The verify() method should not
        be called by the user unless the user has a good reason to do so.
        NOTE: May significantly slow down the code if called frequently.
        """
        raise NotImplementedError("GCGraphABC.verify must be overridden")
