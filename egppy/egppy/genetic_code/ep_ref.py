"""
Mutable EndPoint Reference implementation.
"""

from __future__ import annotations

from typing import Iterable

from egppy.genetic_code.ep_ref_abc import EPRefABC, EPRefsABC, FrozenEPRefABC
from egppy.genetic_code.frozen_ep_ref import FrozenEPRef, FrozenEPRefs


class EPRef(FrozenEPRef, EPRefABC):
    """
    Docstring for EPRef
    """

    def __hash__(self) -> int:
        return hash((self.row, self.idx))

    def __repr__(self) -> str:
        return f"EPRef(row={self.row!r}, idx={self.idx})"


class EPRefs(FrozenEPRefs, EPRefsABC):
    """
    Docstring for EPRefs
    """

    # pylint: disable=super-init-not-called
    def __init__(self, refs: Iterable[FrozenEPRefABC] | None = None):
        self._refs: list[FrozenEPRefABC] = list(refs) if refs else []  # type: ignore

    def __setitem__(self, index: int, value: FrozenEPRefABC) -> None:
        if not isinstance(value, FrozenEPRefABC):
            raise TypeError(f"Invalid value type: {type(value)}")
        self._refs[index] = value

    def __delitem__(self, index: int) -> None:
        del self._refs[index]

    def clear(self) -> None:
        self._refs.clear()

    def insert(self, index: int, value: FrozenEPRefABC) -> None:
        if not isinstance(value, FrozenEPRefABC):
            raise TypeError(f"Invalid value type: {type(value)}")
        self._refs.insert(index, value)

    def __hash__(self) -> int:
        return hash(tuple(self._refs))

    def __repr__(self) -> str:
        return f"EPRefs({self._refs!r})"
