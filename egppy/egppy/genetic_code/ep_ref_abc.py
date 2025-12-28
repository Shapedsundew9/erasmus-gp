"""
Abstract Base Classes for EndPoint References.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Hashable, MutableSequence, Sequence

from egpcommon.common_obj_abc import CommonObjABC
from egppy.genetic_code.c_graph_constants import Row


class FrozenEPRefABC(CommonObjABC, Hashable, metaclass=ABCMeta):
    """Abstract Base Class for Frozen (Immutable) EndPoint Reference."""

    __slots__ = ()
    row: Row
    idx: int

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def __lt__(self, other: object) -> bool: ...


class EPRefABC(FrozenEPRefABC, metaclass=ABCMeta):
    """Abstract Base Class for Mutable EndPoint Reference."""

    __slots__ = ()
    pass


class FrozenEPRefsABC(CommonObjABC, Hashable, Sequence, metaclass=ABCMeta):
    """Abstract Base Class for Frozen Sequence of EndPoint References."""

    __slots__ = ()
    _refs: Sequence[FrozenEPRefABC]

    @abstractmethod
    def __getitem__(self, index: int) -> FrozenEPRefABC:  # type: ignore[override]
        ...

    @abstractmethod
    def __len__(self) -> int: ...


class EPRefsABC(FrozenEPRefsABC, MutableSequence, metaclass=ABCMeta):
    """Abstract Base Class for Mutable Sequence of EndPoint References."""

    __slots__ = ()

    @abstractmethod
    def __setitem__(self, index: int, value: FrozenEPRefABC) -> None:  # type: ignore[override]
        ...

    @abstractmethod
    def insert(self, index: int, value: FrozenEPRefABC) -> None: ...

    @abstractmethod
    def __delitem__(self, index: int) -> None:  # type: ignore[override]
        ...
