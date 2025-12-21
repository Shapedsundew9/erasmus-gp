"""Unit tests for the PsqlType classes."""

import unittest
from datetime import date, datetime, time
from itertools import count
from typing import Any
from uuid import uuid4

from egppy.physics.psql_types import (
    PsqlArray,
    PsqlBigInt,
    PsqlBigIntArray,
    PsqlBool,
    PsqlBoolArray,
    PsqlBytea,
    PsqlChar,
    PsqlDate,
    PsqlDoublePrecision,
    PsqlDoublePrecisionArray,
    PsqlFragmentOrderBy,
    PsqlFragmentWhere,
    PsqlInt,
    PsqlIntArray,
    PsqlIntegral,
    PsqlReal,
    PsqlRealArray,
    PsqlSmallInt,
    PsqlSmallIntArray,
    PsqlTime,
    PsqlTimestamp,
    PsqlType,
    PsqlTypeError,
    PsqlUUID,
    PsqlValueError,
    PsqlVarChar,
    py_cast,
)


# A concrete class for testing PsqlType's abstract methods
class ConcretePsqlType(PsqlType):
    """A concrete implementation of PsqlType for testing purposes."""

    sql_type_name = "CONCRETE"

    def _validate(self, value):
        """Simulate validation by returning the value."""
        # For testing, we can just return the value
        return value


class TestPsqlTypes(unittest.TestCase):
    """Unit tests for the PsqlType classes."""

    def test_inheritance_and_naming(self):
        """Test the class inheritance and sql_type_name for various PsqlTypes."""
        self.assertTrue(issubclass(PsqlSmallInt, PsqlIntegral))
        self.assertEqual(PsqlInt.sql_type_name, "INT4")
        self.assertEqual(PsqlReal.sql_type_name, "REAL")
        self.assertEqual(PsqlUUID.sql_type_name, "UUID")

    def test_literal_uid(self):
        """Test that literal PsqlType objects get unique UIDs."""
        # Reset counter for predictable UIDs
        PsqlType.counter = count(0)
        p1 = PsqlInt(10, is_literal=True)
        p2 = PsqlVarChar("hello", is_literal=True)
        p3 = PsqlInt("col", is_column=True)
        self.assertEqual(p1.uid, 0)
        self.assertEqual(str(p1), "{literal0}")
        self.assertEqual(p2.uid, 1)
        self.assertEqual(str(p2), "{literal1}")
        self.assertEqual(p3.uid, -1)  # Not a literal

    def test_psql_array_base(self):
        """Test that the abstract PsqlArray class cannot be instantiated."""
        # Test abstract base class
        with self.assertRaises(AttributeError):
            # pylint: disable=abstract-class-instantiated
            PsqlArray([1], is_literal=True)  # type: ignore

    def test_psql_bigint(self):
        """Test the PsqlBigInt type and its range constraints."""
        self.assertEqual(PsqlBigInt(10, is_literal=True).value, 10)
        self.assertEqual(
            PsqlBigInt(PsqlBigInt.MAX_VALUE, is_literal=True).value, 9223372036854775807
        )
        self.assertEqual(
            PsqlBigInt(PsqlBigInt.MIN_VALUE, is_literal=True).value, -9223372036854775808
        )
        with self.assertRaises(PsqlValueError):
            PsqlBigInt(PsqlBigInt.MAX_VALUE + 1, is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlBigInt(PsqlBigInt.MIN_VALUE - 1, is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlBigInt(10.5, is_literal=True)

    def test_psql_bigint_array(self):
        """Test the PsqlBigIntArray type."""
        self.assertEqual(
            PsqlBigIntArray([1, 2], is_literal=True).value,
            [PsqlBigInt(1, is_literal=True), PsqlBigInt(2, is_literal=True)],
        )
        with self.assertRaises(PsqlValueError):
            PsqlBigIntArray([1, PsqlBigInt.MAX_VALUE + 1], is_literal=True)
        self.assertEqual(PsqlBigIntArray.get_sql_type_name(), "BIGINT[]")

    def test_psql_bool(self):
        """Test the PsqlBool type."""
        self.assertTrue(PsqlBool(True, is_literal=True).value)
        self.assertFalse(PsqlBool(False, is_literal=True).value)
        with self.assertRaises(PsqlValueError):
            PsqlBool(1, is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlBool("true", is_literal=True)

    def test_psql_bool_array(self):
        """Test the PsqlBoolArray type."""
        self.assertEqual(
            PsqlBoolArray([True, False], is_literal=True).value,
            [PsqlBool(True, is_literal=True), PsqlBool(False, is_literal=True)],
        )
        with self.assertRaises(PsqlValueError):
            PsqlBoolArray([True, 1], is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlBoolArray("not a list", is_literal=True)
        self.assertEqual(PsqlBoolArray.get_sql_type_name(), "BOOL[]")

    def test_psql_bytea(self):
        """Test the PsqlBytea type."""
        b = b"binary data"
        self.assertEqual(PsqlBytea(b, is_literal=True).value, b)
        with self.assertRaises(PsqlValueError):
            PsqlBytea("string data", is_literal=True)

    def test_psql_char(self):
        """Test the PsqlChar type."""
        self.assertEqual(PsqlChar("abc", is_literal=True).value, "abc")
        with self.assertRaises(PsqlValueError):
            PsqlChar(123, is_literal=True)
        # Test with length, though not enforced by default in the provided code
        self.assertEqual(PsqlChar("a", is_literal=True, length=1).value, "a")

    def test_psql_date(self):
        """Test the PsqlDate type."""
        d = date(2025, 9, 21)
        self.assertEqual(PsqlDate(d, is_literal=True).value, d)
        with self.assertRaises(PsqlValueError):
            PsqlDate(datetime.now(), is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlDate("2025-09-21", is_literal=True)

    def test_psql_double_precision(self):
        """Test the PsqlDoublePrecision type."""
        self.assertEqual(PsqlDoublePrecision(10.5, is_literal=True).value, 10.5)
        self.assertEqual(PsqlDoublePrecision(10, is_literal=True).value, 10.0)
        with self.assertRaises(PsqlValueError):
            PsqlDoublePrecision("10.5", is_literal=True)

    def test_psql_double_precision_array(self):
        """Test the PsqlDoublePrecisionArray type."""
        self.assertEqual(
            PsqlDoublePrecisionArray([1.0, 2.0], is_literal=True).value,
            [
                PsqlDoublePrecision(1.0, is_literal=True),
                PsqlDoublePrecision(2.0, is_literal=True),
            ],
        )
        with self.assertRaises(PsqlValueError):
            PsqlDoublePrecisionArray([1.0, "2.0"], is_literal=True)
        self.assertEqual(PsqlDoublePrecisionArray.get_sql_type_name(), "DOUBLE PRECISION[]")

    def test_psql_fragments_and_statements(self):
        """Test the PsqlFragment and PsqlStatement classes."""
        # Test PsqlFragmentWhere
        a = PsqlInt("a", is_column=True)
        one = PsqlInt(1, is_literal=True)
        cond = PsqlBool("{a} > {one}", is_literal=False, param_a=a, param_b=one)
        where = PsqlFragmentWhere(cond)
        self.assertEqual(str(where), "{a} > {one}")
        with self.assertRaises(PsqlValueError):
            PsqlFragmentWhere(PsqlBool(True, is_literal=True))

        # Test PsqlFragmentOrderBy
        col = PsqlInt("my_col", is_column=True)
        order_by_asc = PsqlFragmentOrderBy(col)
        self.assertEqual(str(order_by_asc), "ORDER BY {my_col} ASC")
        order_by_desc = PsqlFragmentOrderBy(col, ascending=False)
        self.assertEqual(str(order_by_desc), "ORDER BY {my_col} DESC")
        with self.assertRaises(PsqlValueError):
            PsqlFragmentOrderBy(
                PsqlInt(
                    "{a} + {b}",
                    is_literal=False,
                    param_a=PsqlInt("a", is_column=True),
                    param_b=PsqlInt("b", is_column=True),
                )
            )

    def test_psql_int(self):
        """Test the PsqlInt type and its range constraints."""
        self.assertEqual(PsqlInt(10, is_literal=True).value, 10)
        self.assertEqual(PsqlInt(PsqlInt.MAX_VALUE, is_literal=True).value, 2147483647)
        self.assertEqual(PsqlInt(PsqlInt.MIN_VALUE, is_literal=True).value, -2147483648)
        with self.assertRaises(PsqlValueError):
            PsqlInt(PsqlInt.MAX_VALUE + 1, is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlInt(PsqlInt.MIN_VALUE - 1, is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlInt(10.5, is_literal=True)

    def test_psql_int_array(self):
        """Test the PsqlIntArray type."""
        self.assertEqual(
            PsqlIntArray([1, 2], is_literal=True).value,
            [PsqlInt(1, is_literal=True), PsqlInt(2, is_literal=True)],
        )
        with self.assertRaises(PsqlValueError):
            PsqlIntArray([1, "2"], is_literal=True)
        self.assertEqual(PsqlIntArray.get_sql_type_name(), "INT4[]")

    def test_psql_real(self):
        """Test the PsqlReal type."""
        self.assertEqual(PsqlReal(10.5, is_literal=True).value, 10.5)
        self.assertEqual(PsqlReal(10, is_literal=True).value, 10.0)
        with self.assertRaises(PsqlValueError):
            PsqlReal("10.5", is_literal=True)

    def test_psql_real_array(self):
        """Test the PsqlRealArray type."""
        self.assertEqual(
            PsqlRealArray([1.0, 2.0], is_literal=True).value,
            [PsqlReal(1.0, is_literal=True), PsqlReal(2.0, is_literal=True)],
        )
        with self.assertRaises(PsqlValueError):
            PsqlRealArray([1.0, "2.0"], is_literal=True)
        self.assertEqual(PsqlRealArray.get_sql_type_name(), "REAL[]")

    def test_psql_smallint(self):
        """Test the PsqlSmallInt type and its range constraints."""
        self.assertEqual(PsqlSmallInt(10, is_literal=True).value, 10)
        self.assertEqual(PsqlSmallInt(PsqlSmallInt.MAX_VALUE, is_literal=True).value, 32767)
        self.assertEqual(PsqlSmallInt(PsqlSmallInt.MIN_VALUE, is_literal=True).value, -32768)
        with self.assertRaises(PsqlValueError):
            PsqlSmallInt(PsqlSmallInt.MAX_VALUE + 1, is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlSmallInt(PsqlSmallInt.MIN_VALUE - 1, is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlSmallInt(10.5, is_literal=True)

    def test_psql_smallint_array(self):
        """Test the PsqlSmallIntArray type."""
        self.assertEqual(
            PsqlSmallIntArray([1, 2], is_literal=True).value,
            [PsqlSmallInt(1, is_literal=True), PsqlSmallInt(2, is_literal=True)],
        )
        with self.assertRaises(PsqlValueError):
            PsqlSmallIntArray([1, PsqlSmallInt.MAX_VALUE + 1], is_literal=True)
        self.assertEqual(PsqlSmallIntArray.get_sql_type_name(), "INT2[]")

    def test_psql_time(self):
        """Test the PsqlTime type."""
        t = time(12, 30, 0)
        self.assertEqual(PsqlTime(t, is_literal=True).value, t)
        with self.assertRaises(PsqlValueError):
            PsqlTime(datetime.now(), is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlTime("12:30:00", is_literal=True)

    def test_psql_timestamp(self):
        """Test the PsqlTimestamp type."""
        dt = datetime.now()
        self.assertEqual(PsqlTimestamp(dt, is_literal=True).value, dt)
        with self.assertRaises(PsqlValueError):
            PsqlTimestamp(date.today(), is_literal=True)
        with self.assertRaises(PsqlValueError):
            PsqlTimestamp("2025-09-21 12:30:00", is_literal=True)

    def test_psql_type_base(self):
        """Test the base functionality of the PsqlType abstract base class."""

        # Test that instantiating an incomplete subclass of an abstract class raises TypeError
        class IncompletePsqlType(PsqlType):
            """An incomplete subclass of PsqlType for testing."""

            sql_type_name = "INCOMPLETE"

        with self.assertRaises(TypeError):
            # This fails because _validate is not implemented
            # pylint: disable=abstract-class-instantiated
            IncompletePsqlType("test", is_literal=True)  # type: ignore
        # Test non-literal value must be a string
        with self.assertRaises(PsqlTypeError):
            ConcretePsqlType(123)

        # Test cannot be both literal and column
        with self.assertRaises(PsqlTypeError):
            ConcretePsqlType("col", is_literal=True, is_column=True)

        # Test column representation
        col_type = PsqlInt("my_col", is_column=True)
        self.assertEqual(str(col_type), "{my_col}")
        self.assertEqual(repr(col_type), "PsqlInt('my_col')")

        # Test expression representation
        a = PsqlInt("a", is_column=True)
        b = PsqlInt("b", is_column=True)
        expr_type = PsqlInt("{a} + {b}", is_literal=False, is_column=False, param_a=a, param_b=b)
        self.assertEqual(str(expr_type), "{a} + {b}")

        # Test internal error for non-string column value
        col_type_any: Any = col_type
        col_type_any.value = 123
        with self.assertRaises(AssertionError):
            str(col_type_any)

        # Test internal error for non-string expression value
        expr_type_any: Any = expr_type
        expr_type_any.is_column = False
        expr_type_any.is_literal = False
        expr_type_any.value = 123
        with self.assertRaises(AssertionError):
            str(expr_type_any)

        # Test equality
        self.assertNotEqual(PsqlInt(1, is_literal=True), PsqlSmallInt(1, is_literal=True))
        self.assertEqual(PsqlInt(1, is_literal=True), PsqlInt(1, is_literal=True))
        self.assertNotEqual(PsqlInt(1, is_literal=True), "not a psql type")

    def test_psql_uuid(self):
        """Test the PsqlUuid type."""
        u = uuid4()
        self.assertEqual(PsqlUUID(u, is_literal=True).value, u)
        with self.assertRaises(PsqlValueError):
            PsqlUUID(str(u), is_literal=True)

    def test_psql_varchar(self):
        """Test the PsqlVarChar type."""
        self.assertEqual(PsqlVarChar("abc", is_literal=True).value, "abc")
        with self.assertRaises(PsqlValueError):
            PsqlVarChar(123, is_literal=True)
        # Test with length, though not enforced by default
        self.assertEqual(PsqlVarChar("abc", is_literal=True, length=10).value, "abc")

    def test_py_cast(self):
        """Test the py_cast function for converting between PsqlType objects."""
        # Successful casts
        self.assertIsInstance(py_cast(PsqlInt(10, is_literal=True), PsqlBigInt), PsqlBigInt)
        self.assertIsInstance(py_cast(PsqlSmallInt(5, is_literal=True), PsqlReal), PsqlReal)
        self.assertEqual(py_cast(PsqlInt(123, is_literal=True), PsqlVarChar).value, "123")

        # Failing casts
        with self.assertRaises(PsqlTypeError):
            py_cast(PsqlVarChar("abc", is_literal=True), PsqlInt)
        with self.assertRaises(PsqlTypeError):
            py_cast(PsqlReal(10.5, is_literal=True), PsqlInt)

        # Test unexpected error during cast
        class BadPsqlType(PsqlType):
            """A PsqlType subclass that always raises an error for testing."""

            sql_type_name = "BAD"

            def _validate(self, value):
                raise RuntimeError("Unexpected validation error")

        with self.assertRaises(PsqlTypeError) as cm:
            py_cast(PsqlInt(1, is_literal=True), BadPsqlType)
        self.assertIn("Unexpected error casting", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
