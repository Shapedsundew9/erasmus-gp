"""The End Point Type Module.

Endpoint types are defined as a tuple of TypesDef objects.

"""

from __future__ import annotations

from re import split
from typing import Iterable, Sequence

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.object_set import ObjectSet

from egppy.gc_graph.end_point.types_def import TypesDef, types_db

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)

# The End Point Type type definition is recursive
EndPointType = tuple[TypesDef, ...]


# The EPT global store
# EPT's are constant and can be shared between interfaces
# Many duplicate EPT's are created in the code and so it is more efficient to store them
# as a tuple of TypesDef objects and share them.
class EPTStore(ObjectSet):
    """The EPT global store."""

    def add(self, tup: EndPointType) -> EndPointType:
        """Add the EPT to the store."""
        assert self.valid_ept(tup), f"Invalid EPT {tup}"
        return super().add(tup)

    def consistency(self) -> None:
        """Check the consistency of the EPT store."""
        self.verify()
        return super().consistency()

    def valid_ept(self, tup: EndPointType) -> bool:
        """Return True if the EPT is valid."""
        assert isinstance(tup, Iterable), f"End point type is not iterable: EPT = {tup}."
        assert all(t in types_db for t in tup), f"End point type is invalid {tup}."
        return True

    def verify(self) -> None:
        """Verify the EPT store."""
        for ept in self:
            self.valid_ept(ept)
        super().verify()


ept_store: EPTStore = EPTStore("End Point Type Store")


def end_point_type(
    type_sequence: Sequence[str | int | TypesDef], _pop: bool = False
) -> EndPointType:
    """Return the EPT as a recursive tuple of TypesDef objects.

    NOTE: If _pop is True type_sequence is a ssumed to be a list that will be modified
    by popping off the first EndPointType. This facility is provided to enable interfaces
    to be efficiently defined.
    """
    assert len(type_sequence) > 0, "The type sequence must have at least one type."
    ts = list(type_sequence) if not _pop else type_sequence
    assert isinstance(ts, list), f"Expected list but found {type(ts)}"
    elmt = ts.pop(0)
    assert isinstance(
        elmt, (str, int, TypesDef)
    ), f"The first element must be a UID or name but found {type(elmt)}"
    # If the element is a UID (or TypesDef) then get the TypesDef object
    # If it is a str it may be a python type string rather than just a name
    if isinstance(elmt, str) and elmt not in types_db:
        return ept_store.add(str_to_ept(elmt))
    typ = types_db[elmt]
    list_ept: list[TypesDef] = [typ]
    list_ept.extend(td for tt in range(typ.tt()) for td in end_point_type(ts, True))
    ept = tuple(list_ept)
    return ept_store.add(ept)


def ept_to_str(ept: EndPointType, _marker: list[int] | None = None) -> str:
    """Return the EPT as a python type style string."""
    assert len(ept) > 0, "The EPT must have at least one type."
    assert isinstance(ept[0], TypesDef), f"Expected TypesDef but found {type(ept[0])}"
    _marker = _marker or [0]
    idx = _marker[0]
    _marker[0] += 1
    tt: int = ept[idx].tt()
    if not tt:
        return ept[idx].name
    return f"{ept[idx].name}[{', '.join(ept_to_str(ept, _marker) for _ in range(tt))}]"


def ept_to_uids(ept: EndPointType) -> tuple[int, ...]:
    """Return the UIDs of the EPT as a tuple."""
    return tuple(tt.uid for tt in ept)


def str_to_ept(type_str: str) -> EndPointType:
    """Return the EPT from a python type style string."""
    # Split out the types into a list of names and push through the end_point_type function
    return end_point_type([s for s in split(r"\W+", type_str) if s])


def ept_to_const(ept: EndPointType) -> str:
    """Return the EPT as a python type style string."""
    assert isinstance(ept[0], TypesDef), f"Expected TypesDef but found {type(ept[0])}"
    if len(ept) == 1:
        return f"types_db['{ept[0].name}']"
    return f"types_db['{ept[0].name}'], {
        ', '.join(ept_to_const(tt) for tt in ept[1:] if isinstance(tt, tuple))}"
