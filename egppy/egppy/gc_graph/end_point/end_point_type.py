"""The End Point Type Class."""

from __future__ import annotations

from re import split
from typing import Sequence

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.tuple_set import TupleSet

from egppy.gc_graph.end_point.types_def import EndPointType, TypesDef, types_db

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# The EPT global store
# EPT's are constant and can be shared between interfaces
# Many duplicate EPT's are created in the code and so it is more efficient to store them
# as a tuple of TypesDef objects and share them.
_ept_store = TupleSet()


def end_point_type(type_sequence: Sequence[str | int | TypesDef | Sequence]) -> EndPointType:
    """Return the EPT as a recursive tuple of TypesDef objects."""
    assert len(type_sequence) > 0, "The type sequence must have at least one type."
    ts = list(type_sequence)
    element = ts.pop(0)
    assert isinstance(
        element, (str, int, TypesDef)
    ), f"The first element must be a UID or name but found {type(element)}"
    typ = types_db[element]
    list_ept: list[tuple[EndPointType | TypesDef, ...] | EndPointType | TypesDef] = [typ]
    list_ept.extend(end_point_type(ts) for tt in range(typ.tt()))
    ept = tuple(list_ept)
    return _ept_store.add(ept)


def ept_to_str(ept: EndPointType) -> str:
    """Return the EPT as a python type style string."""
    assert isinstance(ept[0], TypesDef), f"Expected TypesDef but found {type(ept[0])}"
    if len(ept) == 1:
        return ept[0].name
    return f"{ept[0].name}[{', '.join(ept_to_str(tt) for tt in ept[1:] if isinstance(tt, tuple))}]"


def str_to_ept(type_str: str) -> EndPointType:
    """Return the EPT from a python type style string."""
    # Split out the types into a list of names and push through the end_point_type function
    return end_point_type([s for s in split(r"\W+", type_str) if s])
