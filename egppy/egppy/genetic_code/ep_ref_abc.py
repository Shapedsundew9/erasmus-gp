"""
Abstract Base Classes for EndPoint References.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Hashable, MutableSequence, Sequence

from egpcommon.common_obj_abc import CommonObjABC
from egppy.genetic_code.c_graph_constants import Row


class FrozenEPRefABC(CommonObjABC, Hashable, metaclass=ABCMeta):
    """Frozen EPRef shared base (frozen ABC role for EPRef diamond).

    Role:
        Shared frozen abstract base for the single-reference EPRef diamond.

    Direct Parents:
        `CommonObjABC`, `Hashable`.

    Shared Grandparent:
        This class is the shared grandparent in the EPRef mutable-concrete
        diamond (`FrozenEPRef` and `EPRefABC` converge in `EPRef`).
    """

    __slots__ = ()
    row: Row
    idx: int

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...

    @abstractmethod
    def __lt__(self, other: object) -> bool: ...

    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of the python instanciation
        of the EndPoint Reference such that eval(str(obj)) == obj.
        str(obj) should be as compact as possible

        Returns:
            String representation suitable for python instanciation.
        """
        raise NotImplementedError("FrozenEPRefABC.__str__ must be overridden")


class EPRefABC(FrozenEPRefABC, metaclass=ABCMeta):
    """Mutable EPRef API contract (mutable ABC role for EPRef diamond).

    Role:
        Mutable abstract branch for the single-reference EPRef diamond.

    Direct Parents:
        `FrozenEPRefABC`.

    Shared Grandparent:
        `FrozenEPRefABC` is shared with `FrozenEPRef` and the branches
        converge in `EPRef`.
    """

    __slots__ = ()
    __hash__ = None  # type: ignore[assignment]  # Mutable objects must not be hashable (WP5)


class FrozenEPRefsABC(CommonObjABC, Hashable, Sequence, metaclass=ABCMeta):
    """Frozen EPRefs shared base (frozen ABC role for EPRefs diamond).

    Role:
        Shared frozen abstract base for the reference-sequence EPRefs diamond.

    Direct Parents:
        `CommonObjABC`, `Hashable`, `Sequence`.

    Shared Grandparent:
        This class is the shared grandparent in the EPRefs mutable-concrete
        diamond (`FrozenEPRefs` and `EPRefsABC` converge in `EPRefs`).
    """

    __slots__ = ()
    _refs: Sequence[FrozenEPRefABC]

    @abstractmethod
    def __getitem__(self, index: int) -> FrozenEPRefABC:  # type: ignore[override]
        ...

    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def __str__(self) -> str:
        """Return a string representation of the python instanciation
        of the EndPoint References such that eval(str(obj)) == obj.
        str(obj) should be as compact as possible

        Returns:
            String representation suitable for python instanciation.
        """
        raise NotImplementedError("FrozenEPRefsABC.__str__ must be overridden")


class EPRefsABC(FrozenEPRefsABC, MutableSequence, metaclass=ABCMeta):
    """Mutable EPRefs API contract (mutable ABC role for EPRefs diamond).

    Role:
        Mutable abstract branch for the EPRefs diamond.

    Direct Parents:
        `FrozenEPRefsABC`, `MutableSequence`.

    Shared Grandparent:
        `FrozenEPRefsABC` is shared with `FrozenEPRefs` and the branches
        converge in `EPRefs`.
    """

    __slots__ = ()
    __hash__ = None  # type: ignore[assignment]  # Mutable objects must not be hashable (WP5)

    @abstractmethod
    def __setitem__(self, index: int, value: FrozenEPRefABC) -> None:  # type: ignore[override]
        ...

    @abstractmethod
    def insert(self, index: int, value: FrozenEPRefABC) -> None: ...

    @abstractmethod
    def __delitem__(self, index: int) -> None:  # type: ignore[override]
        ...
