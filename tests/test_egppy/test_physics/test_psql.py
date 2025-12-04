"""Unit tests for PSQL codons and types."""

import unittest
from itertools import count

from egppy.physics.psql import (
    psql_abs,
    psql_add,
    psql_bitwise_and,
    psql_bitwise_not,
    psql_bitwise_or,
    psql_bitwise_xor,
    psql_cbrt,
    psql_concat,
    psql_contains,
    psql_divide,
    psql_eq,
    psql_exp,
    psql_gt,
    psql_gte,
    psql_is_contained_by,
    psql_logical_and,
    psql_logical_not,
    psql_logical_or,
    psql_lshift,
    psql_lt,
    psql_lte,
    psql_modulo,
    psql_multiply,
    psql_ne,
    psql_negate,
    psql_overlaps,
    psql_parentheses,
    psql_rshift,
    psql_sqrt,
    psql_subtract,
)
from egppy.physics.psql_types import (
    PsqlBool,
    PsqlBoolArray,
    PsqlDoublePrecision,
    PsqlInt,
    PsqlIntArray,
    PsqlReal,
    PsqlType,
)


class TestPsqlCodons(unittest.TestCase):
    """Unit tests for PSQL codons and types."""

    def setUp(self):
        # Reset counter for deterministic UIDs
        PsqlType.counter = count(0)

    def test_exceptions(self):
        """Test that type errors are raised for invalid operations."""
        with self.assertRaises(TypeError):
            psql_add(PsqlInt(1), PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_subtract(PsqlInt(1), PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_multiply(PsqlInt(1), PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_divide(PsqlInt(1), PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_modulo(PsqlInt(1), PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_exp(PsqlInt(1), PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_abs(PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_negate(PsqlBool(True))  # type: ignore
        with self.assertRaises(TypeError):
            psql_bitwise_and(PsqlInt(1), PsqlReal(1.0))  # type: ignore
        with self.assertRaises(TypeError):
            psql_bitwise_or(PsqlInt(1), PsqlReal(1.0))  # type: ignore
        with self.assertRaises(TypeError):
            psql_bitwise_xor(PsqlInt(1), PsqlReal(1.0))  # type: ignore
        with self.assertRaises(TypeError):
            psql_bitwise_not(PsqlReal(1.0))  # type: ignore
        with self.assertRaises(TypeError):
            psql_lshift(PsqlInt(1), PsqlReal(1.0))  # type: ignore
        with self.assertRaises(TypeError):
            psql_rshift(PsqlInt(1), PsqlReal(1.0))  # type: ignore
        with self.assertRaises(TypeError):
            psql_sqrt(PsqlInt(1))  # type: ignore
        with self.assertRaises(TypeError):
            psql_cbrt(PsqlInt(1))  # type: ignore
        with self.assertRaises(TypeError):
            psql_concat(PsqlIntArray([1]), PsqlBoolArray([True]))  # type: ignore

    def test_string_rendering(self):
        """Test the string rendering of PSQL codons."""
        # Test simple binary operators
        self.assertEqual(
            str(psql_add(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=0))),
            "{a} + {literal0}",
        )
        self.assertEqual(
            str(psql_subtract(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=1))),
            "{a} - {literal1}",
        )
        self.assertEqual(
            str(psql_multiply(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=2))),
            "{a} * {literal2}",
        )
        self.assertEqual(
            str(psql_divide(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=3))),
            "{a} / {literal3}",
        )
        self.assertEqual(
            str(psql_modulo(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=4))),
            "{a} % {literal4}",
        )
        self.assertEqual(
            str(psql_exp(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=5))),
            "{a} ^ {literal5}",
        )
        self.assertEqual(
            str(psql_lt(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=6))),
            "{a} < {literal6}",
        )
        self.assertEqual(
            str(psql_lte(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=7))),
            "{a} <= {literal7}",
        )
        self.assertEqual(
            str(psql_gt(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=8))),
            "{a} > {literal8}",
        )
        self.assertEqual(
            str(psql_gte(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=9))),
            "{a} >= {literal9}",
        )
        self.assertEqual(
            str(psql_eq(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=10))),
            "{a} = {literal10}",
        )
        self.assertEqual(
            str(psql_ne(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=11))),
            "{a} <> {literal11}",
        )
        self.assertEqual(
            str(
                psql_logical_and(
                    PsqlBool("a", is_column=True), PsqlBool(True, is_literal=True, uid=12)
                )
            ),
            "{a} AND {literal12}",
        )
        self.assertEqual(
            str(
                psql_logical_or(
                    PsqlBool("a", is_column=True), PsqlBool(False, is_literal=True, uid=13)
                )
            ),
            "{a} OR {literal13}",
        )
        self.assertEqual(
            str(
                psql_bitwise_and(PsqlInt("a", is_column=True), PsqlInt(1, is_literal=True, uid=14))
            ),
            "{a} & {literal14}",
        )
        self.assertEqual(
            str(psql_bitwise_or(PsqlInt("a", is_column=True), PsqlInt(1, is_literal=True, uid=15))),
            "{a} | {literal15}",
        )
        self.assertEqual(
            str(
                psql_bitwise_xor(PsqlInt("a", is_column=True), PsqlInt(1, is_literal=True, uid=16))
            ),
            "{a} # {literal16}",
        )
        self.assertEqual(
            str(psql_lshift(PsqlInt("a", is_column=True), PsqlInt(1, is_literal=True, uid=17))),
            "{a} << {literal17}",
        )
        self.assertEqual(
            str(psql_rshift(PsqlInt("a", is_column=True), PsqlInt(1, is_literal=True, uid=18))),
            "{a} >> {literal18}",
        )
        self.assertEqual(
            str(
                psql_contains(
                    PsqlIntArray("a", is_column=True), PsqlIntArray([1], is_literal=True, uid=19)
                )
            ),
            "{a} @> {literal19}",
        )
        self.assertEqual(
            str(
                psql_is_contained_by(
                    PsqlIntArray("a", is_column=True), PsqlIntArray([1], is_literal=True, uid=20)
                )
            ),
            "{a} <@ {literal20}",
        )
        self.assertEqual(
            str(
                psql_overlaps(
                    PsqlIntArray("a", is_column=True), PsqlIntArray([1], is_literal=True, uid=21)
                )
            ),
            "{a} && {literal21}",
        )
        self.assertEqual(
            str(
                psql_concat(
                    PsqlIntArray("a", is_column=True), PsqlIntArray([1], is_literal=True, uid=22)
                )
            ),
            "{a} || {literal22}",
        )

        # Test unary operators
        self.assertEqual(str(psql_abs(PsqlInt("a", is_column=True))), "@{a}")
        self.assertEqual(str(psql_negate(PsqlInt("a", is_column=True))), "-({a})")
        self.assertEqual(str(psql_bitwise_not(PsqlInt("a", is_column=True))), "~{a}")
        self.assertEqual(str(psql_sqrt(PsqlDoublePrecision("a", is_column=True))), "sqrt({a})")
        self.assertEqual(str(psql_cbrt(PsqlDoublePrecision("a", is_column=True))), "cbrt({a})")
        self.assertEqual(str(psql_logical_not(PsqlBool("a", is_column=True))), "NOT {a}")

        # Test parentheses
        self.assertEqual(str(psql_parentheses(PsqlInt("a", is_column=True))), "{a}")
        self.assertEqual(str(psql_parentheses(PsqlInt(1, is_literal=True, uid=23))), "{literal23}")
        self.assertEqual(
            str(
                psql_parentheses(
                    psql_add(PsqlInt("a", is_column=True), PsqlInt(2, is_literal=True, uid=24))
                )
            ),
            "({a} + {literal24})",
        )


if __name__ == "__main__":
    unittest.main()
