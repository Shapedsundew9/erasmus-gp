"""The Interface Module."""

from __future__ import annotations

from collections.abc import Hashable, MutableSequence, Sequence
from hashlib import sha256
from typing import Generator

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.object_set import ObjectSet

from egppy.c_graph.end_point.end_point_type import EndPointType, ept_store
from egppy.c_graph.end_point.types_def import TypesDef

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class _tuple(tuple):
    """A tuple class to avoid _tuple() == tuple()."""

    def __hash__(self) -> int:
        """Return the hash of the tuple."""
        return 123456789

    def __eq__(self, value: object) -> bool:
        """Return True only if the value is this tuple."""
        return value is self


# Interface constants
# NOTE that the NULL_INTERFACE is a tuple of an empty tuple to avoid
# matching with an empty interface. EndPointTypes cannot be an empty tuple.
INTERFACE_MAX_LENGTH: int = 256
NULL_INTERFACE: _tuple = _tuple()

# The Interface type definition
Interface = Sequence[EndPointType]
MutableInterface = MutableSequence[EndPointType]
AnyInterface = Interface | MutableInterface
RawInterface = (
    Sequence[Sequence[str]]  # e.g. [['list', 'int'], ['int']]
    | Sequence[Sequence[int]]  # e.g. [[1, 2], [2]]
    | Sequence[EndPointType]  # e.g. [(TypesDef(), TypesDef()), (TypesDef(),)]
    | Sequence[str]  # e.g. ['list[int]', 'int'] or ['list', 'int', 'int]
    | Sequence[int]  # e.g. [1, 2, 2]
    | Sequence[TypesDef]  # e.g. [TypesDef(), TypesDef(), TypesDef()]
    | Generator[Sequence[str], None, None]
    | Generator[Sequence[int], None, None]
    | Generator[EndPointType, None, None]
    | Generator[str, None, None]
    | Generator[int, None, None]
    | Generator[TypesDef, None, None]
)


# The interface global store
# Interfaces are constant and can be shared between GC's
# Many duplicate interfaces are created in the code and so it is more efficient to store them
# as a tuple of EndPointType objects and share them.
class InterfaceStore(ObjectSet):
    """The interface global store."""

    def add(self, tup: Interface) -> Interface:
        """Add the interface to the store."""
        assert self.valid_interface(tup), f"Invalid interface {tup}"
        return super().add(tup)

    def consistency(self) -> None:
        """Check the consistency of the interface store."""
        ept_store.consistency()
        self.verify()
        return super().consistency()

    def valid_interface(self, tup: Interface) -> bool:
        """Return True if the interface is valid."""
        assert len(tup) <= INTERFACE_MAX_LENGTH, "Interface has too many endpoints."
        try:
            for ept in tup:
                ept_store.valid_ept(ept)
        except AssertionError as e:
            raise AssertionError(f"Invalid interface has an invalid endpoint {tup}. {e}") from None
        return True

    def verify(self) -> None:
        """Verify the interface store."""
        for iface in self:
            self.valid_interface(iface)
        super().verify()


interface_store = InterfaceStore("Interface Store")
interface_store.add(NULL_INTERFACE)


def interface(iface: RawInterface) -> Interface:
    """Return the interface as a tuple of EndPointType objects."""
    return interface_store.add(tuple(mutable_interface(iface)))


def interface_to_parameters(iface: AnyInterface) -> str:
    """Return the interface as a string in the format '(i0: name, i1: name, ..., in: name)'."""
    return f"({', '.join(f'i{idx}: {str(ept)}' for idx, ept in enumerate(iface))})"


def interface_to_list_str(iface: AnyInterface) -> list[str]:
    """Return the interface as a string in the format '(i0: name, i1: name, ..., in: name)'."""
    return [str(ept) for ept in iface]


def interface_to_uids(iface: AnyInterface) -> list[int]:
    """Return the interface as a list of endpoint type UIDs."""
    return [uid for ept in iface for uid in ept.to_uids()]


def is_abstract_interface(iface: AnyInterface) -> bool:
    """Return True if the interface is abstract."""
    return any(ept.is_abstract_endpoint() for ept in iface)


def mutable_interface(iface: RawInterface) -> MutableInterface:
    """Return the interface as a list of EndPointType objects."""
    # It could be an interface in the store then return the list of EPT's.
    # This is a common pattern in the code and so is more efficient to handle here.
    if isinstance(iface, Hashable) and iface in interface_store:
        return list(iface)  # type: ignore
    _interface = list(iface)
    if not _interface:
        return []
    # All elements in an interface must be the same type.
    if isinstance(_interface[0], (str, int, TypesDef)):
        retval = []
        while _interface:
            # Pop EndPointTypes from the RawInterface until it is empty
            retval.append(end_point_type(_interface, True))  # type: ignore
        assert (
            len(retval) <= INTERFACE_MAX_LENGTH
        ), f"Interface has too many endpoints: {len(retval)}."
        return retval
    # Must be a list of EndPointType-like objects
    assert (
        len(_interface) <= INTERFACE_MAX_LENGTH
    ), f"Interface has too many endpoints: {len(_interface)}."
    return [end_point_type(ept) for ept in _interface if isinstance(ept, Sequence)]


def interface_hash(iface: AnyInterface) -> bytes:
    """Return the sha256 of the interface endpoint type UIDs in the order they are
    defined for the interface."""
    return sha256(
        b"".join(uid.to_bytes(4, "big", signed=True) for uid in interface_to_uids(iface))
    ).digest()


def interface_to_types_idx(iface: AnyInterface) -> tuple[tuple[tuple[int, ...], ...], bytes]:
    """Return the interface as an ordered tuple of endpoint types and indices into it."""
    tuple_iface = tuple(tuple(td.uid for td in ept) for ept in iface)
    ordered_types = tuple(sorted(set(tuple_iface)))
    return ordered_types, bytes(ordered_types.index(ept) for ept in tuple_iface)


def types_idx_to_interface(ordered_types: Sequence[Sequence[int]], indices: bytes) -> Interface:
    """Return the interface from an ordered tuple of endpoint types and indices into it."""
    # The ordered_types is a tuple of tuples of endpoint type UIDs == an interface
    # (but not *the* interface)
    ordered_epts = interface(ordered_types)
    return tuple(ordered_epts[idx] for idx in indices)


def interface_type_hash(iface: AnyInterface) -> bytes:
    """Return the sha256 of the ordered unique interface endpoint type UIDs."""
    ordered_types, _ = interface_to_types_idx(iface)
    return sha256(
        b"".join(uid.to_bytes(4, "big", signed=True) for ept in ordered_types for uid in ept)
    ).digest()


def verify_interface(iface: AnyInterface) -> None:
    """Verify the interface. Either the interface is in the store or it is a
    mutable sequence of valid end point types."""
    if isinstance(iface, Hashable):
        assert iface in interface_store, f"Invalid interface {iface}. Expected to be in the store."
    else:
        try:
            for ept in iface:
                ept_store.valid_ept(ept)
        except AssertionError as e:
            raise AssertionError(f"Invalid interface {iface}. {e}") from None
