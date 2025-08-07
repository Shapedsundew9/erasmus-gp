"""Row iterators."""

from collections import namedtuple
from logging import DEBUG, Logger, NullHandler, getLogger
from typing import Any, Callable, Iterable, Literal, Self

from psycopg2.extensions import cursor

_logger: Logger = getLogger(__name__)
_logger.addHandler(NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(DEBUG)


class BaseIter:
    """Iterator returning a container of decoded values from values.

    The order of the containers returned is the same as the rows of values in values.
    Each value is decoded by the registered conversion function (see register_conversion()) or
    unchanged if no conversion has been registered.
    """

    def __init__(self, columns: Iterable[str], values, _table, code: str = "decode") -> None:
        """Initialise.

        Args
        ----
        columns (iter(str)): Column names for each of the rows in values.
        values  (row_iter): Iterator over rows (tuples) with values in the order as columns.
        """
        self.values = values
        self.conversions: list[Callable[[Any], Any] | None] = [
            _table._conversions[column][code] for column in columns
        ]
        self.columns: Iterable[str] = columns

    def __iter__(self) -> Self:
        """Self iteration."""
        return self

    def __next__(self) -> Any:
        """Never gets run."""
        raise NotImplementedError

    def __del__(self) -> None:
        if isinstance(self.values, cursor):
            self.values.close()


class GenIter(BaseIter):
    """Iterator returning a generator for decoded values from values."""

    def __next__(self) -> Any:
        """Return next value."""
        # No strict because pk may be tagged on the end of the values but not in the columns
        # deepcode ignore unguarded~next~call: next() is guarded by the outer next() call
        return (v if f is None else f(v) for f, v in zip(self.conversions, next(self.values)))


class TupleIter(BaseIter):
    """Iterator returning a tuple for decoded values from values."""

    def __next__(self) -> Any:
        """Return next value."""
        return tuple(
            # No strict because pk may be tagged on the end of the values but not in the columns
            # deepcode ignore unguarded~next~call: next() is guarded by the outer next() call
            (v if f is None else f(v) for f, v in zip(self.conversions, next(self.values)))
        )


class NamedTupleIter(BaseIter):
    """Iterator returning a namedtuple for decoded values from values."""

    def __init__(self, columns: Iterable[str], values, _table, code: str = "decode") -> None:
        super().__init__(columns, values, _table, code)
        self.namedtuple = namedtuple("row", columns)

    def __next__(self) -> Any:
        """Return next value."""
        return self.namedtuple(
            # No strict because pk may be tagged on the end of the values but not in the columns
            # deepcode ignore unguarded~next~call: next() is guarded by the outer next() call
            (v if f is None else f(v) for f, v in zip(self.conversions, next(self.values)))
        )


class DictIter(BaseIter):
    """Iterator returning a dict for decoded values from values."""

    def __next__(self) -> Any:
        """Return next value."""
        return {
            c: v if f is None else f(v)
            # No strict because pk may be tagged on the end of the values but not in the columns
            # deepcode ignore unguarded~next~call: next() is guarded by the outer next() call
            for c, f, v in zip(self.columns, self.conversions, next(self.values))
        }


RowIter = TupleIter | NamedTupleIter | GenIter | DictIter
RawCType = Literal["tuple", "namedtuple", "dict"]
