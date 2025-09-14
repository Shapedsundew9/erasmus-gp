"""Functions for PSQL codons."""

from numbers import Complex, Number, Rational

from egppy.physics.psql_types import PsqlBool, PsqlType


def psql_lt(i0: PsqlType, i1: PsqlType) -> PsqlBool:
    """Return the less-than comparison of two PSQL expressions."""
    if i0.is_literal and i1.is_literal and isinstance(i1.value, type(i0.value)):
        return PsqlBool(i0.value < i1.value, is_literal=True)
    return PsqlBool(f"{i0} < {i1}")


def psql_lte(i0: PsqlType, i1: PsqlType) -> PsqlBool:
    """Return the less-than-or-equal comparison of two PSQL expressions."""
    if i0.is_literal and i1.is_literal and isinstance(i1.value, type(i0.value)):
        return PsqlBool(i0.value <= i1.value, is_literal=True)
    return PsqlBool(f"{i0} <= {i1}")


def psql_gt(i0: PsqlType, i1: PsqlType) -> PsqlBool:
    """Return the greater-than comparison of two PSQL expressions."""
    if i0.is_literal and i1.is_literal and isinstance(i1.value, type(i0.value)):
        return PsqlBool(i0.value > i1.value, is_literal=True)
    return PsqlBool(f"{i0} > {i1}")


def psql_gte(i0: PsqlType, i1: PsqlType) -> PsqlBool:
    """Return the greater-than-or-equal comparison of two PSQL expressions."""
    if i0.is_literal and i1.is_literal and isinstance(i1.value, type(i0.value)):
        return PsqlBool(i0.value >= i1.value, is_literal=True)
    return PsqlBool(f"{i0} >= {i1}")


def psql_eq(i0: PsqlType, i1: PsqlType) -> PsqlBool:
    """Return the equality comparison of two PSQL expressions."""
    if i0.is_literal and i1.is_literal and isinstance(i1.value, type(i0.value)):
        return PsqlBool(i0.value == i1.value, is_literal=True)
    return PsqlBool(f"{i0} = {i1}")


def psql_ne(i0: PsqlType, i1: PsqlType) -> PsqlBool:
    """Return the not-equal comparison of two PSQL expressions."""
    if i0.is_literal and i1.is_literal and isinstance(i1.value, type(i0.value)):
        return PsqlBool(i0.value != i1.value, is_literal=True)
    return PsqlBool(f"{i0} <> {i1}")


import math

# --- Numeric Operators ---
from egppy.physics.psql_types import PsqlDoublePrecision, PsqlIntegral, PsqlNumeric


def psql_add(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Complex), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Complex), "PsqlNumeric value must be a number."
        return type(i0)(i0.value + i1.value, is_literal=True)
    return type(i0)(f"{i0} + {i1}")


def psql_subtract(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Complex), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Complex), "PsqlNumeric value must be a number."
        return type(i0)(i0.value - i1.value, is_literal=True)
    return type(i0)(f"{i0} - {i1}")


def psql_multiply(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Complex), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Complex), "PsqlNumeric value must be a number."
        return type(i0)(i0.value * i1.value, is_literal=True)
    return type(i0)(f"{i0} * {i1}")


def psql_divide(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Complex), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Complex), "PsqlNumeric value must be a number."
        return type(i0)(i0.value / i1.value, is_literal=True)
    return type(i0)(f"{i0} / {i1}")


def psql_modulo(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Rational), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Rational), "PsqlNumeric value must be a number."
        return type(i0)(i0.value % i1.value, is_literal=True)
    return type(i0)(f"{i0} % {i1}")


def psql_exp(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Complex), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Complex), "PsqlNumeric value must be a number."
        return type(i0)(i0.value**i1.value, is_literal=True)
    return type(i0)(f"{i0} ^ {i1}")


def psql_abs(i0: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal:
        assert isinstance(i0.value, Complex), "PsqlNumeric value must be a number."
        return type(i0)(abs(i0.value), is_literal=True)
    return type(i0)(f"@{i0}")


def psql_negate(i0: PsqlNumeric) -> PsqlNumeric:
    if i0.is_literal:
        assert isinstance(i0.value, Complex), "PsqlNumeric value must be a number."
        return type(i0)(-i0.value, is_literal=True)
    return type(i0)(f"-({i0})")


# --- Integral Operators ---
def psql_bitwise_and(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    if i0.is_literal and i1.is_literal:
        return type(i0)(i0.value & i1.value, is_literal=True)
    return type(i0)(f"{i0} & {i1}")


def psql_bitwise_or(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    if i0.is_literal and i1.is_literal:
        return type(i0)(i0.value | i1.value, is_literal=True)
    return type(i0)(f"{i0} | {i1}")


def psql_bitwise_xor(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    if i0.is_literal and i1.is_literal:
        return type(i0)(i0.value ^ i1.value, is_literal=True)
    return type(i0)(f"{i0} # {i1}")


def psql_bitwise_not(i0: PsqlIntegral) -> PsqlIntegral:
    if i0.is_literal:
        return type(i0)(~i0.value, is_literal=True)
    return type(i0)(f"~{i0}")


def psql_lshift(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    if i0.is_literal and i1.is_literal:
        return type(i0)(i0.value << i1.value, is_literal=True)
    return type(i0)(f"{i0} << {i1}")


def psql_rshift(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    if i0.is_literal and i1.is_literal:
        return type(i0)(i0.value >> i1.value, is_literal=True)
    return type(i0)(f"{i0} >> {i1}")


# --- Double Precision Operators ---
def psql_sqrt(i0: PsqlDoublePrecision) -> PsqlDoublePrecision:
    if i0.is_literal:
        return type(i0)(math.sqrt(i0.value), is_literal=True)
    return type(i0)(f"sqrt({i0})")


def psql_cbrt(i0: PsqlDoublePrecision) -> PsqlDoublePrecision:
    if i0.is_literal:
        return type(i0)(i0.value ** (1 / 3), is_literal=True)
    return type(i0)(f"cbrt({i0})")


# --- Boolean Operators ---
def psql_logical_and(i0: PsqlBool, i1: PsqlBool) -> PsqlBool:
    if i0.is_literal and i1.is_literal:
        return PsqlBool(i0.value and i1.value, is_literal=True)
    return PsqlBool(f"{i0} AND {i1}")


def psql_logical_or(i0: PsqlBool, i1: PsqlBool) -> PsqlBool:
    if i0.is_literal and i1.is_literal:
        return PsqlBool(i0.value or i1.value, is_literal=True)
    return PsqlBool(f"{i0} OR {i1}")


def psql_logical_not(i0: PsqlBool) -> PsqlBool:
    if i0.is_literal:
        return PsqlBool(not i0.value, is_literal=True)
    return PsqlBool(f"NOT {i0}")


# --- Array Operators ---
from egppy.physics.psql_types import PsqlArray


def psql_contains(i0: PsqlArray, i1: PsqlArray) -> PsqlBool:
    if i0.is_literal and i1.is_literal:
        return PsqlBool(set(i1.value).issubset(set(i0.value)), is_literal=True)
    return PsqlBool(f"{i0} @> {i1}")


def psql_is_contained_by(i0: PsqlArray, i1: PsqlArray) -> PsqlBool:
    if i0.is_literal and i1.is_literal:
        return PsqlBool(set(i0.value).issubset(set(i1.value)), is_literal=True)
    return PsqlBool(f"{i0} <@ {i1}")


def psql_overlaps(i0: PsqlArray, i1: PsqlArray) -> PsqlBool:
    if i0.is_literal and i1.is_literal:
        return PsqlBool(bool(set(i0.value) & set(i1.value)), is_literal=True)
    return PsqlBool(f"{i0} && {i1}")


def psql_concat(i0: PsqlArray, i1: PsqlArray) -> PsqlArray:
    if i0.is_literal and i1.is_literal:
        return type(i0)(i0.value + i1.value, is_literal=True)
    return type(i0)(f"{i0} || {i1}")
