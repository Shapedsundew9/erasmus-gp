"""Abstract base class for GC graph objects."""
from __future__ import annotations
from collections.abc import MutableMapping
from abc import abstractmethod
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCGraphABC(MutableMapping):
    """Abstract Base Class for Genetic Code Graphs.
    
    The graph abstract base class, GCGraphABC, is the base class for all genetic code graph objects.
    GC graph objects define connections between interfaces.
    
   
    """
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        """Constructor for GCGraphABC"""
        raise NotImplementedError("GCGraphABC.__init__ must be overridden")

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Equality comparison must be implemented in the derived class."""
        raise NotImplementedError("GCGraphABC.__eq__ must be overridden")

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        """Inequality comparison must be implemented in the derived class."""
        raise NotImplementedError("GCGraphABC.__ne__ must be overridden")

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
