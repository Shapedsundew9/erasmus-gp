"""The list interface module."""
from egppy.storage.cache.cacheable_dirty_list_base import CacheableDirtyListBase
from egppy.storage.cache.cache_illegal import CacheIllegal
from egppy.gc_graph.interface_base import InterfaceBase
from egppy.gc_graph.interface_abc import InterfaceABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ListInterface(  # type: ignore
    CacheIllegal, CacheableDirtyListBase, InterfaceBase, InterfaceABC):
    """List Interface class.

    The ListInterface class is a subclass of list and InterfaceABC.
    It is a list-like object that is used to represent the list interface.
    """
