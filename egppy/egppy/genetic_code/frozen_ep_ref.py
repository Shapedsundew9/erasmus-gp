"""
Frozen EndPoint Reference implementation.
"""

from __future__ import annotations

from collections.abc import Iterable

from egpcommon.common_obj import CommonObj
from egpcommon.deduplication import ref_store
from egppy.genetic_code.c_graph_constants import DstRow, Row, SrcRow
from egppy.genetic_code.ep_ref_abc import FrozenEPRefABC, FrozenEPRefsABC


class FrozenEPRef(CommonObj, FrozenEPRefABC):
    """
    Docstring for FrozenEPRef
    """

    __slots__ = ("row", "idx", "_hash")

    def __init__(self, row: Row, idx: int):
        self.row = row
        self.idx = idx
        self._hash = hash((row, idx))

    def consistency(self) -> None:
        self.verify()

    def verify(self) -> None:
        if not isinstance(self.row, (SrcRow, DstRow)):
            raise TypeError(f"Invalid row type: {type(self.row)}")
        if not isinstance(self.idx, int):
            raise TypeError(f"Invalid idx type: {type(self.idx)}")
        if self.idx < 0:
            raise ValueError(f"Invalid idx value: {self.idx}")
        if self.idx >= 0:
            raise ValueError(f"Invalid idx value: {self.idx}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrozenEPRefABC):
            raise NotImplementedError("FrozenEPRef.__eq__ requires a FrozenEPRefABC instance")
        return self.row == other.row and self.idx == other.idx

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, FrozenEPRefABC):
            raise NotImplementedError("FrozenEPRef.__lt__ requires a FrozenEPRefABC instance")
        if self.row != other.row:
            return self.row < other.row
        return self.idx < other.idx

    def __hash__(self) -> int:
        return self._hash

    def __repr__(self) -> str:
        return f"FrozenEPRef(row={self.row!r}, idx={self.idx})"


class FrozenEPRefs(CommonObj, FrozenEPRefsABC):
    """
    Docstring for FrozenEPRefs
    """

    __slots__ = ("_refs", "_hash")

    def __init__(self, refs: Iterable[FrozenEPRefABC]):
        self._refs = tuple(
            # pylint: disable=unidiomatic-typecheck
            ref_store[t if type(t) is FrozenEPRef else FrozenEPRef(t.row, t.idx)]
            for t in refs
        )
        self._hash = hash(self._refs)

    def consistency(self) -> None:
        self.verify()
        for ref in self._refs:
            ref.consistency()

    def verify(self) -> None:
        if not isinstance(self._refs, tuple):
            raise TypeError(f"Invalid refs type: {type(self._refs)}")
        for ref in self._refs:
            if not isinstance(ref, FrozenEPRefABC):
                raise TypeError(f"Invalid ref type: {type(ref)}")

    def __getitem__(self, index: int) -> FrozenEPRefABC:
        return self._refs[index]

    def __iter__(self):
        """Efficient iterator over the references."""
        for item in self._refs:
            yield item

    def __len__(self) -> int:
        return len(self._refs)

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrozenEPRefsABC):
            raise NotImplementedError("FrozenEPRefs.__eq__ requires a FrozenEPRefsABC instance")
        if len(self) != len(other):
            return False
        assert isinstance(other, FrozenEPRefsABC), "Type checker hint"
        return all(s == o for s, o in zip(self._refs, other._refs))

    def __repr__(self) -> str:
        return f"FrozenEPRefs({self._refs!r})"
