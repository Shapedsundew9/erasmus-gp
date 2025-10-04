"""Functions for PSQL codons."""

import math
from numbers import Integral, Real

from egppy.physics.psql_types import (
    PsqlArray,
    PsqlBool,
    PsqlDoublePrecision,
    PsqlIntegral,
    PsqlNumeric,
    PsqlType,
)


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


def psql_add(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    """Return the sum of two PSQL numeric expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlNumeric):
        raise TypeError(f"Cannot add {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Real), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(i0.value + i1.value, is_literal=True)
    return suptype(f"{i0} + {i1}")


def psql_subtract(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    """Return the difference of two PSQL numeric expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlNumeric):
        raise TypeError(f"Cannot subtract {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Real), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(i0.value - i1.value, is_literal=True)
    return suptype(f"{i0} - {i1}")


def psql_multiply(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    """Return the product of two PSQL numeric expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlNumeric):
        raise TypeError(f"Cannot multiply {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Real), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(i0.value * i1.value, is_literal=True)
    return suptype(f"{i0} * {i1}")


def psql_divide(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    """Return the division of two PSQL numeric expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlNumeric):
        raise TypeError(f"Cannot divide {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Real), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(i0.value / i1.value, is_literal=True)
    return suptype(f"{i0} / {i1}")


def psql_modulo(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    """Return the modulo of two PSQL numeric expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlNumeric):
        raise TypeError(f"Cannot modulo {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Real), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(i0.value % i1.value, is_literal=True)
    return suptype(f"{i0} % {i1}")


def psql_exp(i0: PsqlNumeric, i1: PsqlNumeric) -> PsqlNumeric:
    """Return the exponentiation of two PSQL numeric expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlNumeric):
        raise TypeError(f"Cannot exponentiate {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i1.value, Real), "PsqlNumeric value must be a number."
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(i0.value**i1.value, is_literal=True)
    return suptype(f"{i0} ^ {i1}")


def psql_abs(i0: PsqlNumeric) -> PsqlNumeric:
    """Return the absolute value of a PSQL numeric expression."""
    if not issubclass(suptype := type(i0), PsqlNumeric):
        raise TypeError(f"Cannot apply abs to {type(i0)}")
    if i0.is_literal:
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(abs(i0.value), is_literal=True)
    return suptype(f"@{i0}")


def psql_negate(i0: PsqlNumeric) -> PsqlNumeric:
    """Return the negation of a PSQL numeric expression."""
    if not issubclass(suptype := type(i0), PsqlNumeric):
        raise TypeError(f"Cannot apply negation to {type(i0)}")
    if i0.is_literal:
        assert isinstance(i0.value, Real), "PsqlNumeric value must be a number."
        return suptype(-i0.value, is_literal=True)
    return suptype(f"-({i0})")


# --- Integral Operators ---
def psql_bitwise_and(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    """Return the bitwise AND of two PSQL integral expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlIntegral):
        raise TypeError(f"Cannot AND {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i0.value, Integral), "PsqlIntegral value must be an integer."
        assert isinstance(i1.value, Integral), "PsqlIntegral value must be an integer."
        return suptype(i0.value & i1.value, is_literal=True)
    return suptype(f"{i0} & {i1}")


def psql_bitwise_or(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    """Return the bitwise OR of two PSQL integral expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlIntegral):
        raise TypeError(f"Cannot OR {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i0.value, Integral), "PsqlIntegral value must be an integer."
        assert isinstance(i1.value, Integral), "PsqlIntegral value must be an integer."
        return suptype(i0.value | i1.value, is_literal=True)
    return suptype(f"{i0} | {i1}")


def psql_bitwise_xor(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    """Return the bitwise XOR of two PSQL integral expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlIntegral):
        raise TypeError(f"Cannot XOR {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i0.value, Integral), "PsqlIntegral value must be an integer."
        assert isinstance(i1.value, Integral), "PsqlIntegral value must be an integer."
        return suptype(i0.value ^ i1.value, is_literal=True)
    return suptype(f"{i0} # {i1}")


def psql_bitwise_not(i0: PsqlIntegral) -> PsqlIntegral:
    """Return the bitwise NOT of a PSQL integral expression."""
    if not issubclass(suptype := type(i0), PsqlIntegral):
        raise TypeError(f"Cannot apply bitwise NOT to {type(i0)}")
    if i0.is_literal:
        assert isinstance(i0.value, Integral), "PsqlIntegral value must be an integer."
        return suptype(~i0.value, is_literal=True)
    return suptype(f"~{i0}")


def psql_lshift(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    """Return the left shift of two PSQL integral expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlIntegral):
        raise TypeError(f"Cannot left shift {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i0.value, Integral), "PsqlIntegral value must be an integer."
        assert isinstance(i1.value, Integral), "PsqlIntegral value must be an integer."
        return suptype(i0.value << i1.value, is_literal=True)
    return suptype(f"{i0} << {i1}")


def psql_rshift(i0: PsqlIntegral, i1: PsqlIntegral) -> PsqlIntegral:
    """Return the right shift of two PSQL integral expressions."""
    suptype = type(i0) if issubclass(type(i0), type(i1)) else type(i1)
    if not issubclass(suptype, PsqlIntegral):
        raise TypeError(f"Cannot right shift {type(i0)} and {type(i1)}")
    if i0.is_literal and i1.is_literal:
        assert isinstance(i0.value, Integral), "PsqlIntegral value must be an integer."
        assert isinstance(i1.value, Integral), "PsqlIntegral value must be an integer."
        return suptype(i0.value >> i1.value, is_literal=True)
    return suptype(f"{i0} >> {i1}")


# --- Double Precision Operators ---
def psql_sqrt(i0: PsqlDoublePrecision) -> PsqlDoublePrecision:
    """Return the square root of a PSQL double precision expression."""
    if not issubclass(suptype := type(i0), PsqlDoublePrecision):
        raise TypeError(f"Cannot apply sqrt to {type(i0)}")
    if i0.is_literal:
        assert isinstance(i0.value, Real), "PsqlDoublePrecision value must be a real number."
        return suptype(math.sqrt(i0.value), is_literal=True)
    return suptype(f"sqrt({i0})")


def psql_cbrt(i0: PsqlDoublePrecision) -> PsqlDoublePrecision:
    """Return the cube root of a PSQL double precision expression."""
    if not issubclass(suptype := type(i0), PsqlDoublePrecision):
        raise TypeError(f"Cannot apply cbrt to {type(i0)}")
    if i0.is_literal:
        assert isinstance(i0.value, Real), "PsqlDoublePrecision value must be a real number."
        return suptype(i0.value ** (1 / 3), is_literal=True)
    return suptype(f"cbrt({i0})")


# --- Boolean Operators ---
def psql_logical_and(i0: PsqlBool, i1: PsqlBool) -> PsqlBool:
    """Return the logical AND of two PSQL boolean expressions."""
    if i0.is_literal and i1.is_literal:
        assert isinstance(i0.value, bool), "PsqlBool value must be a boolean."
        assert isinstance(i1.value, bool), "PsqlBool value must be a boolean."
        return PsqlBool(i0.value and i1.value, is_literal=True)
    return PsqlBool(f"{i0} AND {i1}")


def psql_logical_or(i0: PsqlBool, i1: PsqlBool) -> PsqlBool:
    """Return the logical OR of two PSQL boolean expressions."""
    if i0.is_literal and i1.is_literal:
        assert isinstance(i0.value, bool), "PsqlBool value must be a boolean."
        assert isinstance(i1.value, bool), "PsqlBool value must be a boolean."
        return PsqlBool(i0.value or i1.value, is_literal=True)
    return PsqlBool(f"{i0} OR {i1}")


def psql_logical_not(i0: PsqlBool) -> PsqlBool:
    """Return the logical NOT of a PSQL boolean expression."""
    if i0.is_literal:
        assert isinstance(i0.value, bool), "PsqlBool value must be a boolean."
        return PsqlBool(not i0.value, is_literal=True)
    return PsqlBool(f"NOT {i0}")


def psql_contains(i0: PsqlArray, i1: PsqlArray) -> PsqlBool:
    """Return whether the first PSQL array contains the second."""
    if i0.is_literal and i1.is_literal:
        return PsqlBool(set(i1.value).issubset(set(i0.value)), is_literal=True)
    return PsqlBool(f"{i0} @> {i1}")


def psql_is_contained_by(i0: PsqlArray, i1: PsqlArray) -> PsqlBool:
    """Return whether the first PSQL array is contained by the second."""
    if i0.is_literal and i1.is_literal:
        return PsqlBool(set(i0.value).issubset(set(i1.value)), is_literal=True)
    return PsqlBool(f"{i0} <@ {i1}")


def psql_overlaps(i0: PsqlArray, i1: PsqlArray) -> PsqlBool:
    """Return whether the two PSQL arrays overlap."""
    if i0.is_literal and i1.is_literal:
        return PsqlBool(bool(set(i0.value) & set(i1.value)), is_literal=True)
    return PsqlBool(f"{i0} && {i1}")


def psql_concat(i0: PsqlArray, i1: PsqlArray) -> PsqlArray:
    """Return the concatenation of two PSQL arrays."""
    if i0.is_literal and i1.is_literal:
        return type(i0)(i0.value + i1.value, is_literal=True)
    return type(i0)(f"{i0} || {i1}")


# -- Other operations
def psql_parentheses(i0: PsqlType) -> PsqlType:
    """Return the PSQL expression wrapped in parentheses."""
    return type(i0)(f"({i0})") if not (i0.is_literal or i0.is_column) else i0
