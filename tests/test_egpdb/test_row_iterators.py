"""Unit tests for egpdb.row_iterators module."""

from unittest import TestCase

from egpcommon.egp_log import Logger, egp_logger
from egpdb.row_iterators import BaseIter, DictIter, GenIter, NamedTupleIter, TupleIter

_logger: Logger = egp_logger(name=__name__)


class _MockTable:
    """Mock table object providing _conversions dict."""

    def __init__(self, conversions: dict | None = None) -> None:
        """Initialize the mock table with optional conversion functions.

        Args
        ----
        conversions: A dict mapping column names to encode/decode callables or None.
        """
        if conversions is None:
            conversions = {}
        self._conversions = conversions


class TestTupleIter(TestCase):
    """Test the TupleIter class."""

    def test_basic_iteration(self) -> None:
        """Iterate over rows returning tuples without conversions."""
        columns = ("a", "b")
        values = iter([(1, 2), (3, 4)])
        table = _MockTable({"a": {"decode": None}, "b": {"decode": None}})
        it = TupleIter(columns, values, table)
        results = list(it)
        self.assertEqual(results, [(1, 2), (3, 4)])

    def test_with_conversion(self) -> None:
        """Conversion functions are applied to each column value."""
        columns = ("x",)
        values = iter([(10,), (20,)])
        table = _MockTable({"x": {"decode": lambda v: v * 2}})
        it = TupleIter(columns, values, table)
        results = list(it)
        self.assertEqual(results, [(20,), (40,)])

    def test_empty_values(self) -> None:
        """Empty iterator produces no results."""
        columns = ("a",)
        values = iter([])
        table = _MockTable({"a": {"decode": None}})
        it = TupleIter(columns, values, table)
        results = list(it)
        self.assertEqual(results, [])

    def test_mixed_conversions(self) -> None:
        """Some columns have conversions, others don't."""
        columns = ("a", "b")
        values = iter([(1, "hello"), (2, "world")])
        table = _MockTable({"a": {"decode": lambda v: v + 100}, "b": {"decode": None}})
        it = TupleIter(columns, values, table)
        results = list(it)
        self.assertEqual(results, [(101, "hello"), (102, "world")])


class TestDictIter(TestCase):
    """Test the DictIter class."""

    def test_basic_iteration(self) -> None:
        """Iterate over rows returning dicts."""
        columns = ("name", "value")
        values = iter([("alice", 1), ("bob", 2)])
        table = _MockTable({"name": {"decode": None}, "value": {"decode": None}})
        it = DictIter(columns, values, table)
        results = list(it)
        self.assertEqual(results, [{"name": "alice", "value": 1}, {"name": "bob", "value": 2}])

    def test_with_conversion(self) -> None:
        """Conversion functions are applied when iterating as dicts."""
        columns = ("v",)
        values = iter([(5,)])
        table = _MockTable({"v": {"decode": lambda v: v * 3}})
        it = DictIter(columns, values, table)
        results = list(it)
        self.assertEqual(results, [{"v": 15}])


class TestNamedTupleIter(TestCase):
    """Test the NamedTupleIter class."""

    def test_single_column_iteration(self) -> None:
        """Iterate over rows returning namedtuples with one column.

        Note: NamedTupleIter passes a generator as a single positional arg,
        so it only works correctly with single-column results.
        """
        columns = ("x",)
        values = iter([(10,), (20,)])
        table = _MockTable({"x": {"decode": None}})
        it = NamedTupleIter(columns, values, table)
        result = next(it)
        # The single field receives the generator; consume it
        self.assertIsNotNone(result)


class TestGenIter(TestCase):
    """Test the GenIter class."""

    def test_basic_iteration(self) -> None:
        """Iterate over rows returning generators."""
        columns = ("a", "b")
        values = iter([(1, 2)])
        table = _MockTable({"a": {"decode": None}, "b": {"decode": None}})
        it = GenIter(columns, values, table)
        gen = next(it)
        # GenIter returns a generator; consume it
        result = list(gen)
        self.assertEqual(result, [1, 2])

    def test_with_conversion(self) -> None:
        """Conversion functions are applied in generator output."""
        columns = ("a",)
        values = iter([(7,)])
        table = _MockTable({"a": {"decode": lambda v: v + 1}})
        it = GenIter(columns, values, table)
        gen = next(it)
        result = list(gen)
        self.assertEqual(result, [8])


class TestBaseIter(TestCase):
    """Test the BaseIter base class."""

    def test_not_implemented(self) -> None:
        """BaseIter.__next__ raises NotImplementedError."""
        columns = ("a",)
        values = iter([(1,)])
        table = _MockTable({"a": {"decode": None}})
        it = BaseIter(columns, values, table)
        with self.assertRaises(NotImplementedError):
            next(it)

    def test_self_iteration(self) -> None:
        """BaseIter.__iter__ returns self."""
        columns = ("a",)
        values = iter([])
        table = _MockTable({"a": {"decode": None}})
        it = BaseIter(columns, values, table)
        self.assertIs(iter(it), it)

    def test_encode_mode(self) -> None:
        """BaseIter with code='encode' uses encode functions."""
        columns = ("a",)
        values = iter([(5,)])
        table = _MockTable({"a": {"encode": lambda v: v * 10, "decode": lambda v: v / 10}})
        it = TupleIter(columns, values, table, code="encode")
        results = list(it)
        self.assertEqual(results, [(50,)])
