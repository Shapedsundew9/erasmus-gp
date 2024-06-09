"""Dirty Dictionary Genetic Code Base Class module."""
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_graph.gc_graph_abc import GCGraphABC
from egppy.storage.cache.cacheable_dirty_dict import CacheableDirtyDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class DirtyDictBaseGCGraph(CacheableDirtyDict, GCGraphABC):
    """Dirty Dictionary Genetic Code Graph Base Class.
    Builtin dictionaries are fast but use a lot of space. This class is a base class
    for genetic code objects using builtin dictionary methods without wrapping them.
    As a consequence when the dictionary is modified the object is not automatically
    marked as dirty, this must be done manually by the user using the dirty() method.
    """
