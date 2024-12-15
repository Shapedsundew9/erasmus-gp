"""TupleSet class.

A tuple set is a set of tuples. It is a set of unique tuples that may be referenced
in many places. The intent is to reduce memory consumption when a lot of duplicate
tuples are used in a program.

>>> a = (2, 4, 5)
>>> b = (2, 4, 5)
>>> id(a)
128822992399424
>>> id(b)
128822991659840

"""

from collections.abc import Collection


class TupleSet(Collection):
    """TupleSet class.

    A tuple set is a set of tuples. It is a set of unique tuples that may be referenced
    in many places. The intent is to reduce memory consumption when a lot of duplicate
    tuples are used in a program."""

    def __init__(self) -> None:
        """Initialize a TupleSet object."""
        self._tuples: dict[tuple, tuple] = {}

    def add(self, tup: tuple) -> tuple:
        """Add a tuple to the set."""
        # If the tuple is already in the set, return the existing tuple.
        return self._tuples.setdefault(tup, tup)

    def remove(self, tup: tuple) -> None:
        """Remove a tuple from the set."""
        del self._tuples[tup]

    def __contains__(self, tup) -> bool:
        """Check if a tuple is in the set."""
        return tup in self._tuples

    def __len__(self):
        """Return the number of tuples in the set."""
        return len(self._tuples)

    def __iter__(self):
        """Return an iterator over the tuples in the set."""
        return iter(self._tuples)
