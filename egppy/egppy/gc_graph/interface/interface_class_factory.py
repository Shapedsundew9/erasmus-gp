"""The list interface module."""
from egppy.gc_graph.interface.interface_mixin import InterfaceMixin
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.egp_typing import EndPointType
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TupleInterface(tuple[EndPointType, ...], InterfaceMixin, InterfaceABC):
    """A tuple interface object.

    The TupleInterface class is a subclass of tuple and InterfaceMixin.
    It is a tuple-like object of integers representing endpoint types.
    """

# To be used for all empty interface references
EMPTY_INTERFACE: TupleInterface = TupleInterface()
