"""The End Point Type Module.

Endpoint types are defined as a tuple of TypesDef objects.

"""

from __future__ import annotations

from itertools import count
from re import split
from typing import Iterable, Sequence

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.object_set import ObjectSet

from egppy.c_graph.end_point.types_def import TypesDef, types_db

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# The generic tuple type UID
_TUPLE_UID: int = types_db["tuple"].uid


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
        if not isinstance(tup, Iterable):
            raise ValueError(f"End point type is not iterable: EPT = {tup}.")
        if not all(t in types_db for t in tup):
            raise ValueError(f"End point type is invalid {tup}.")
        return True

    def verify(self) -> None:
        """Verify the EPT store."""
        for ept in self:
            self.valid_ept(ept)
        super().verify()


ept_store: EPTStore = EPTStore("End Point Type Store")


# This "store" needs to be replaced with a proper store
_EPT_UID_STORE: dict[str, int] = {}
_EPT_UID_COUNT = count()


def get_ept_uid(type_sequence: tuple[TypesDef, ...], name: str) -> int:
    """Retrieve the EPT UID
    This comes from the local store or is fetched from the remote (global store).
    """
    if len(type_sequence) == 1:
        return type_sequence[0].uid
    if name not in _EPT_UID_STORE:
        _EPT_UID_STORE[name] = next(_EPT_UID_COUNT)
    return _EPT_UID_STORE[name]


def end_point_type(
    type_sequence: Sequence[str | int | TypesDef] | str,
) -> EndPointType:
    """Return the EPT as a tuple of TypesDef objects."""
    if isinstance(type_sequence, str):
        return ept_store.add(EndPointType(from_str(type_sequence)))
    return ept_store.add(EndPointType(from_type_sequence(type_sequence)))


def from_type_sequence(
    type_sequence: Sequence[str | int | TypesDef], _pop: bool = False
) -> tuple[TypesDef, ...]:
    """Return the EPT as a recursive tuple of TypesDef objects.

    If the endpoint type is valid and not in the store then it is added.

    NOTE: If _pop is True type_sequence is assumed to be a list that will be modified
    by popping off the first EndPointType. This facility is provided to enable interfaces
    to be efficiently defined.
    """
    if len(type_sequence) <= 0:
        raise ValueError("The type sequence must have at least one type.")
    if isinstance(type_sequence, str):
        raise ValueError("The type sequence must not be a str.")
    ts = list(type_sequence) if not _pop else type_sequence
    if not isinstance(ts, list):
        raise ValueError(f"Expected list but found {type(ts)}")
    elmt = ts.pop(0)
    if not isinstance(elmt, (str, int, TypesDef)):
        raise ValueError(f"The first element must be a UID or name but found {type(elmt)}")
    # If the element is a UID (or TypesDef) then get the TypesDef object
    # If it is a str it may be a python type string rather than just a name
    if isinstance(elmt, str) and elmt not in types_db and "[" in elmt:
        return ept_store.add(EndPointType(from_str(elmt))).ept
    typ = types_db[elmt]
    if typ.tt() > len(ts):
        raise ValueError(f"Expected at least {typ.tt()} types but found {len(ts)}.")
    list_ept: list[TypesDef] = [typ]
    list_ept.extend(td for tt in range(typ.tt()) for td in from_type_sequence(ts, True))
    return tuple(list_ept)


def to_const(ept: tuple[TypesDef, ...]) -> str:
    """Return the EPT as a python type style string."""
    assert isinstance(ept[0], TypesDef), f"Expected TypesDef but found {type(ept[0])}"
    if len(ept) == 1:
        return f"types_db['{ept[0].name}']"
    return f"types_db['{ept[0].name}'], {', '.join(
        to_const(tt) for tt in ept[1:] if isinstance(tt, tuple))}"


def to_str(ept: tuple[TypesDef, ...], _marker: list[int] | None = None) -> str:
    """Return the EPT as a python type style string.

    Args:
        ept: The EPT as a tuple of TypesDef objects.
        _marker: A list of one integer to keep track of the current position in the EPT.
    """
    assert len(ept) > 0, "The EPT must have at least one type."
    assert isinstance(ept[0], TypesDef), f"Expected TypesDef but found {type(ept[0])}"
    _marker = _marker or [0]
    idx = _marker[0]
    _marker[0] += 1
    td = ept[idx]
    tt: int = td.tt()
    if not tt:
        return td.name
    # Tuples require a special case
    ext = ", ..." if td.uid == _TUPLE_UID else ""
    return f"{td.name}[{', '.join(to_str(ept, _marker) for _ in range(tt))}{ext}]"


def from_str(type_str: str) -> tuple[TypesDef, ...]:
    """Return the EPT from a python type style string."""
    # Split out the types into a list of names and push through the end_point_type function
    # NB: Split will remove any spaces, periods (including tuple ... notation) and commas
    return from_type_sequence([s for s in split(r"\W+", type_str) if s], True)


class EndPointType:
    """The End Point Type.

    An End Point Type is a tuple of TypesDef objects. It is used to define the types of
    the inputs and outputs of an end point.
    """

    def __init__(self, type_sequence: tuple[TypesDef, ...]) -> None:
        self.ept = type_sequence
        self.str = to_str(self.ept)
        self._hash = hash(self.str)
        self.uid = get_ept_uid(type_sequence, self.str)

    def __eq__(self, value: object) -> bool:
        """Check if the object is equal to the value."""
        if not isinstance(value, EndPointType):
            return False
        return self.uid == value.uid

    def __hash__(self) -> int:
        """Return the hash of the object."""
        return self._hash

    def __repr__(self) -> str:
        return f"EndPointType({self.ept})"

    def __str__(self) -> str:
        return to_str(self.ept)

    def to_uids(self) -> tuple[int, ...]:
        """Return the UIDs of the EPT as a tuple."""
        return tuple(tt.uid for tt in self.ept)

    def is_abstract_endpoint(self) -> bool:
        """Return True if the EPT contains an abstract type."""
        return any(tt.abstract for tt in self.ept)
