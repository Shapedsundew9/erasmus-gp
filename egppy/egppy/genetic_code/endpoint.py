"""
Mutable EndPoint Implementation.

This module provides the concrete implementation of the EndPoint abstract base class,
which represents connection points (nodes) in genetic code graphs. EndPoints act as
either sources (outputs) or destinations (inputs) with associated types and references
to other endpoints.

Key Features:
    - Mutable endpoint representation for connection graphs
    - Type-safe endpoint connections with validation
    - Support for both source and destination endpoints
    - Deep copying for mutability and independence

Classes:
    EndPoint: Concrete implementation using builtin collections
    SrcEndPoint: Convenience class for source endpoints
    DstEndPoint: Convenience class for destination endpoints

Connection Rules:
    - Source endpoints may connect to 0, 1, or multiple destination endpoints
    - Destination endpoints may only connect to a single source endpoint
    - Endpoints can only connect to endpoints of the same type
    - References must be bidirectional (facilitated by connect() method)

See Also:
    - c_graph_abc.py: Abstract base class for connection graphs (module docstring)
    - endpoint_abc.py: Abstract base class definition
    - interface.py: Collection of endpoints (interfaces)
    - c_graph.py: Connection graph using interfaces
"""

from __future__ import annotations

from egppy.genetic_code.c_graph_constants import EPCls, Row
from egppy.genetic_code.endpoint_abc import EndPointABC, FrozenEndPointABC
from egppy.genetic_code.ep_ref import EPRef, EPRefs
from egppy.genetic_code.ep_ref_abc import FrozenEPRefABC
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint


class EndPoint(FrozenEndPoint, EndPointABC):
    """Mutable EndPoint implementation (mutable concrete role).

    Role:
        Mutable concrete class at the convergence point of the EndPoint diamond.

    Direct Parents:
        `FrozenEndPoint`, `EndPointABC`.

    Shared Grandparent:
        `FrozenEndPointABC` is shared by both parent branches and parent order
        is intentional for MRO-safe initialization.
    """

    __copy__ = None  # type: ignore (reset to default behaviour)
    __deepcopy__ = None  # type: ignore (reset to default behaviour)

    """Initialize the endpoint.

    This constructor supports multiple initialization patterns:

    1. Copy from another FrozenEndPointABC instance:
        EndPoint(other_endpoint)

    2. Initialize from a 5-tuple:
        EndPoint((row, idx, cls, typ, refs))

    3. Initialize from explicit arguments (4 or 5 args):
        EndPoint(row, idx, cls, typ)
        EndPoint(row, idx, cls, typ, refs)

    The typ argument can be either a TypesDef instance or a string key that
    will be looked up in types_def_store. The refs argument, if provided,
    will be deep copied to ensure mutability and independence.

    Args:
        *args: Variable arguments supporting the patterns described above.

    Raises:
        TypeError: If arguments don't match any supported initialization pattern.
    """

    def _cache_hash(self) -> None:
        """Mutable endpoints do not cache their hash.

        Overrides FrozenEndPoint._cache_hash() so that calling super().__init__()
        does not pre-compute a hash for mutable objects (FR-002).
        """
        self._hash = 0

    @staticmethod
    def _convert_refs(refs_arg) -> EPRefs:
        if refs_arg is None:
            return EPRefs()
        if isinstance(refs_arg, EPRefs):
            # Deep copy refs
            return EPRefs([EPRef(ref.row, ref.idx) for ref in refs_arg])

        refs_list = []
        for ref in refs_arg:
            if isinstance(ref, FrozenEPRefABC):
                refs_list.append(EPRef(ref.row, ref.idx))
            elif isinstance(ref, (list, tuple)) and len(ref) == 2:
                refs_list.append(EPRef(ref[0], ref[1]))
            else:
                raise TypeError(f"Invalid ref format: {ref}")
        return EPRefs(refs_list)

    __hash__ = None  # type: ignore[assignment]  # Mutable objects must not be hashable (WP5)

    def clr_refs(self) -> EndPointABC:
        """Clear all references in the endpoint.
        Returns:
            EndPointABC: Self with all references cleared.
        """
        self.refs.clear()
        return self

    def connect(self, other: FrozenEndPointABC) -> None:
        """Connect this endpoint to another endpoint.

        Establishes a unidirectional reference from this endpoint to the other endpoint.
        The behavior differs based on endpoint class:

        - Destination endpoints (DST): Replaces refs with a single reference to other.
        - Source endpoints (SRC): Appends a reference to other to the refs list.

        Note: This creates only a unidirectional connection. For bidirectional connections,
        call connect() on both endpoints or use higher-level methods in Interface/CGraph.

        Args:
            other (FrozenEndPointABC): The endpoint to connect to.
        """
        assert isinstance(other, FrozenEndPointABC), "Can only connect to another EndPoint instance"
        if self.cls == EPCls.DST:
            self.refs = EPRefs([EPRef(other.row, other.idx)])
        else:
            self.refs.append(EPRef(other.row, other.idx))

    def ref_shift(self, shift: int) -> EndPointABC:
        """Shift all references in the endpoint by a specified amount.
        Args:
            shift: The amount to shift each reference.
        Returns:
            EndPointABC: Self with all references shifted.
        """
        for ref in self.refs:
            assert isinstance(ref.idx, int), "Reference index must be an integer"
            ref.idx += shift
        return self

    def set_ref(self, row: Row, idx: int, append: bool = False) -> EndPointABC:
        """Set or append to the references for an endpoint.

        This method always sets (replaces) the reference of a destination endpoint
        to the specified row and index. For a source endpoint, it appends the new reference
        to the existing list of references if append is True; otherwise, it replaces the
        entire list with the new reference.

        Args:
            row (Row): The row of the endpoint to reference.
            idx (int): The index of the endpoint to reference.
            append (bool): If True and the endpoint is a source, append the new reference;
                           otherwise, replace the references. Defaults to False.
        Returns:
            EndPointABC: Self with the reference set.
        """
        if self.cls == EPCls.SRC and append:
            self.refs.append(EPRef(row, idx))
        else:
            self.refs = EPRefs([EPRef(row, idx)])
        return self


class SrcEndPoint(EndPoint):
    """Source Endpoint convenience class.

    A convenience class for creating source (SRC) endpoints with simplified initialization.
    Automatically sets the endpoint class to SRC, reducing boilerplate when creating
    output endpoints.

    Args:
        row (Row): The row identifier.
        idx (int): The endpoint index within the row.
        typ (TypesDef | str): The endpoint type.
        refs (list[list[str | int]] | None): Optional initial references. Defaults to None.

    Example:
        src_ep = SrcEndPoint('O', 0, 'int')
        src_ep = SrcEndPoint('O', 1, types_def_store['float'], [[I', 0]])
    """

    def __init__(self, *args) -> None:
        """Initialize the source endpoint.

        Args:
            *args: (row, idx, typ) or (row, idx, typ, refs)
        """
        super().__init__(args[0], args[1], EPCls.SRC, args[2], args[3] if len(args) == 4 else None)


class DstEndPoint(EndPoint):
    """Destination Endpoint convenience class.

    A convenience class for creating destination (DST) endpoints with simplified initialization.
    Automatically sets the endpoint class to DST, reducing boilerplate when creating
    input endpoints.

    Args:
        row (Row): The row identifier.
        idx (int): The endpoint index within the row.
        typ (TypesDef | str): The endpoint type.
        refs (list[list[str | int]] | None): Optional initial references. Defaults to None.

    Example:
        dst_ep = DstEndPoint('I', 0, 'int')
        dst_ep = DstEndPoint('I', 1, types_def_store['float'], [['O', 0]])
    """

    def __init__(self, *args) -> None:
        """Initialize the destination endpoint.

        Args:
            *args: (row, idx, typ) or (row, idx, typ, refs)
        """
        super().__init__(args[0], args[1], EPCls.DST, args[2], args[3] if len(args) == 4 else None)
