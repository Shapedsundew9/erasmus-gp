"""The list interface module."""
from egppy.storage.cache.cacheable_list import CacheableList
from egppy.storage.cache.cacheable_dirty_list import CacheableDirtyList
from egppy.gc_graph.interface.interface_base import InterfaceBase
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.interface.interface_illegal import InterfaceIllegal
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ListInterface(InterfaceIllegal, CacheableList, InterfaceBase, InterfaceABC):  # type: ignore
    """Interface class based on a CacheableList."""


class DirtyListInterface(  # type: ignore
    InterfaceIllegal, CacheableDirtyList, InterfaceBase, InterfaceABC):
    """Interface class based on a CacheableDirtyList."""


# To be used for all empty interface references
EMPTY_INTERFACE: ListInterface = ListInterface()
