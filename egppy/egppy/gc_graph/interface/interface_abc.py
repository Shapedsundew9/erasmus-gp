"""The Interface Abstract Base Class module."""
from __future__ import annotations
from collections.abc import MutableSequence
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InterfaceABC(CacheableObjABC, MutableSequence):
    """Interface Abstract Base Class.

    The Interface Abstract Base Class, InterfaceABC, is the base class for all interface objects.
    Interface objects define the properties of an interface.
    It is a subclass of MutableSequence (broadly list-like) and must implement all the primitives
    as required by MutableSequence. HOWEVER, InterfaceABC stubs out the methods that are not
    supported by
    interface objects. This is because the interface objects are designed to be lightweight
    and do not support all the methods of MutableSequence (just most of them). The most notable
    missing methods are pop, popitem, and clear.
    """
