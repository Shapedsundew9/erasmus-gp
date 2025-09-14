"""The psql_types module defines the types for interacting with
a PostgreSQL database as a physical genetic code storage. This is the
role of the selectors."""

from abc import ABC, abstractmethod
from datetime import date, datetime, time
from itertools import count
from typing import Any
from uuid import UUID

from numpy.ma.extras import isin

# This module is the sole module for type definitions for PSQL types
# allowing EGP code to be refactored and renamed without impacting codon signatures.


# --- Custom Exceptions ---
class PsqlValueError(ValueError):
    """Value is invalid for the specific PSQL type."""

    pass


class PsqlTypeError(TypeError):
    """Type mismatch during PSQL expression construction."""

    pass


class PsqlRuntimeError(RuntimeError):
    """Runtime error during PSQL expression construction or evaluation."""

    pass


# --- Base PSQL Type ---
class PsqlType(ABC):
    """Abstract base class for PSQL type representations."""

    # Using __slots__ for potentially many instances created during GP
    __slots__ = ("value", "is_literal", "is_column", "uid")

    # Class variable holding the standard PSQL type name
    sql_type_name: str = "PsqlType"  # Override in subclasses
    counter: count = count(0)  # For unique IDs if needed

    def __init__(self, value: Any, is_literal: bool = False, is_column: bool = False):
        """Initialize the PsqlType with a value.

        If both is_literal and is_column are False then the value is treated as an expression.

        Args:
            value:      The Python variable value to use as a literal or the
                        column name as a string.
            is_literal: If True, 'value' is treated as a literal value
            is_column:  If True, 'value' is treated as a column name

        """
        if not is_literal and not isinstance(value, str):
            raise PsqlTypeError(
                "Non-literal PsqlType value must be a string (column name or expression),"
                f"got {type(value).__name__}"
            )
        if is_literal and is_column:
            raise PsqlTypeError("PsqlType cannot be both literal and column.")
        self.value = self._validate(value) if is_literal else value
        self.is_literal: bool = is_literal
        self.is_column: bool = is_column
        self.uid: int = next(self.counter) if is_literal else -1

    def __eq__(self, other):
        # Basic equality for potential use in GP state
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    def __str__(self):
        """String representation for embedding in EGPDB Table PSQL expressions."""
        if self.is_column:
            assert isinstance(
                self.value, str
            ), "Internal error: PsqlType column value must be a string."
            # Write the column name in bracers as per EGPDB convention
            return f"{{{self.value}}}"
        if self.is_literal:
            return "literal{self.uid}"
        # Must be an expression
        assert (
            isinstance(self.value, str) and not self.is_literal and not self.is_column
        ), "Internal error: PsqlType value must be a string expression if not literal or column."
        return self.value

    @abstractmethod
    def _validate(self, value):
        """Validate the Python value against PSQL type constraints.
        Return the validated (possibly type-converted) value or raise PsqlValueError.
        """
        raise NotImplementedError


class PsqlNumber(PsqlType):
    """Base class for numeric PSQL types."""

    pass


class PsqlIntegral(PsqlNumber):
    """Base class for integral PSQL types."""

    pass


class PsqlNumeric(PsqlNumber):
    """Base class for numeric PSQL types that are not integral."""

    pass


# --- Concrete PSQL Types ---
class PsqlBool(PsqlType):
    """Boolean type."""

    sql_type_name = "BOOL"

    def _validate(self, value):
        if not isinstance(value, bool):
            # Allow 0/1? GP might generate ints. Let's be strict for now.
            raise PsqlValueError(f"Invalid value for BOOL: {value!r}. Must be True or False.")
        return value


class PsqlSmallInt(PsqlIntegral):
    """Small integer type (16 bits)"""

    sql_type_name = "INT2"
    MIN_VALUE = -32768
    MAX_VALUE = 32767

    def _validate(self, value):
        if not isinstance(value, int):
            raise PsqlValueError(f"Invalid type for SMALLINT: {type(value).__name__}. Must be int.")
        if not self.MIN_VALUE <= value <= self.MAX_VALUE:
            raise PsqlValueError(
                f"Value {value} out of range for SMALLINT ({self.MIN_VALUE} to {self.MAX_VALUE})."
            )
        return value


class PsqlInt(PsqlIntegral):
    """Integer type (32 bits)"""

    sql_type_name = "INT4"
    MIN_VALUE = -2147483648
    MAX_VALUE = 2147483647

    def _validate(self, value):
        if not isinstance(value, int):
            raise PsqlValueError(f"Invalid type for INTEGER: {type(value).__name__}. Must be int.")
        if not self.MIN_VALUE <= value <= self.MAX_VALUE:
            raise PsqlValueError(
                f"Value {value} out of range for INTEGER ({self.MIN_VALUE} to {self.MAX_VALUE})."
            )
        return value


class PsqlBigInt(PsqlIntegral):
    """Big integer type (64 bits)"""

    sql_type_name = "BIGINT"
    MIN_VALUE = -9223372036854775808
    MAX_VALUE = 9223372036854775807

    def _validate(self, value):
        if not isinstance(value, int):
            raise PsqlValueError(f"Invalid type for BIGINT: {type(value).__name__}. Must be int.")
        if not self.MIN_VALUE <= value <= self.MAX_VALUE:
            raise PsqlValueError(
                f"Value {value} out of range for BIGINT ({self.MIN_VALUE} to {self.MAX_VALUE})."
            )
        return value


class PsqlReal(PsqlNumeric):
    """Single precision floating point type (32 bits)"""

    sql_type_name = "REAL"

    def _validate(self, value):
        if not isinstance(value, (float, int)):  # Allow ints to become floats
            raise PsqlValueError(
                f"Invalid type for REAL: {type(value).__name__}. Must be float or int."
            )
        return float(value)  # Store as float


class PsqlDoublePrecision(PsqlNumeric):
    """Double precision floating point type (64 bits)"""

    sql_type_name = "DOUBLE PRECISION"

    def _validate(self, value):
        if not isinstance(value, (float, int)):
            raise PsqlValueError(
                f"Invalid type for DOUBLE PRECISION: {type(value).__name__}. Must be float or int."
            )
        return float(value)


class PsqlChar(PsqlType):
    """Character type (fixed length)"""

    sql_type_name = "CHAR"  # Note: CHAR has fixed length semantics in PSQL

    # Add length validation if needed, passed to __init__?
    def __init__(self, value, length=None):  # Example if length needed
        self.length = length
        super().__init__(value)

    def _validate(self, value):
        if not isinstance(value, str):
            raise PsqlValueError(f"Invalid type for CHAR: {type(value).__name__}. Must be str.")
        # Optional: Add length check if self.length is set
        # if self.length is not None and len(value) > self.length:
        #    raise PsqlValueError(f"Value '{value}' too long for CHAR({self.length}).")
        return value


class PsqlVarChar(PsqlType):
    """Variable character type (length is not fixed)"""

    sql_type_name = "VARCHAR"

    # Add length validation if needed
    def __init__(self, value, length=None):  # Example if length needed
        self.length = length
        super().__init__(value)

    def _validate(self, value):
        if not isinstance(value, str):
            raise PsqlValueError(f"Invalid type for VARCHAR: {type(value).__name__}. Must be str.")
        # Optional: Add length check if self.length is set
        # if self.length is not None and len(value) > self.length:
        #    raise PsqlValueError(f"Value '{value}' too long for VARCHAR({self.length}).")
        return value


class PsqlDate(PsqlType):
    """Date type (no time)"""

    sql_type_name = "DATE"

    def _validate(self, value):
        if not isinstance(value, date):
            # Allow datetime objects? Truncate? Be strict for now.
            raise PsqlValueError(f"Invalid type for DATE: {type(value).__name__}. Must be date.")
        return value


class PsqlTime(PsqlType):
    """Time type (no date)"""

    sql_type_name = "TIME"

    def _validate(self, value):
        if not isinstance(value, time):
            raise PsqlValueError(f"Invalid type for TIME: {type(value).__name__}. Must be time.")
        return value


class PsqlTimestamp(PsqlType):
    """Timestamp type (date and time)"""

    sql_type_name = "TIMESTAMP"  # Assumes 'timestamp without time zone'

    def _validate(self, value):
        if not isinstance(value, datetime):
            raise PsqlValueError(
                f"Invalid type for TIMESTAMP: {type(value).__name__}. Must be datetime"
            )
        return value


class PsqlUuid(PsqlType):
    """UUID type"""

    sql_type_name = "UUID"

    def _validate(self, value):
        if not isinstance(value, UUID):
            raise PsqlValueError(f"Invalid type for UUID: {type(value).__name__}. Must be UUID.")
        return value


class PsqlBytea(PsqlType):
    """Binary data type"""

    sql_type_name = "BYTEA"

    def _validate(self, value):
        if not isinstance(value, bytes):
            raise PsqlValueError(f"Invalid type for BYTEA: {type(value).__name__}. Must be bytes.")
        return value


# --- Array Types ---
class PsqlArray(PsqlType):
    """Base for array types."""

    sql_type_name = "ARRAY"  # Needs element type
    element_type: type[PsqlType]  # Defined in subclasses

    def _validate(self, value):
        if not isinstance(value, list):
            raise PsqlValueError(
                f"Invalid type for {self.sql_type_name}: {type(value).__name__}. Must be list."
            )
        # Validate each element using the specific element type's validator
        validated_elements = []
        for i, item in enumerate(value):
            try:
                # Create an instance of the element type to trigger its validation
                validated_element = self.element_type(item).value
                validated_elements.append(validated_element)
            except PsqlValueError as e:
                raise PsqlValueError(
                    f"Invalid element at index {i} for {self.sql_type_name}: {e}"
                ) from e
        return validated_elements

    @classmethod
    def get_sql_type_name(cls):
        """Get the full PSQL type name including element type."""
        # Produces e.g., "INT4[]"
        return f"{cls.element_type.sql_type_name}[]"


# Concrete Array examples (Integer types, Float types, Char types)
class PsqlBoolArray(PsqlArray):
    """Boolean array type (1 bit)"""

    element_type = PsqlBool
    sql_type_name = element_type.sql_type_name + "[]"


class PsqlIntArray(PsqlArray):
    """Integer array type (32 bits)"""

    element_type = PsqlInt
    sql_type_name = element_type.sql_type_name + "[]"


class PsqlSmallIntArray(PsqlArray):
    """Small integer array type (16 bits)"""

    element_type = PsqlSmallInt
    sql_type_name = element_type.sql_type_name + "[]"


class PsqlBigIntArray(PsqlArray):
    """Big integer array type (64 bits)"""

    element_type = PsqlBigInt
    sql_type_name = element_type.sql_type_name + "[]"


class PsqlRealArray(PsqlArray):
    """Single precision floating point array type (32 bits)"""

    element_type = PsqlReal
    sql_type_name = element_type.sql_type_name + "[]"


class PsqlDoublePrecisionArray(PsqlArray):
    """Double precision floating point array type (64 bits)"""

    element_type = PsqlDoublePrecision
    sql_type_name = element_type.sql_type_name + "[]"


# --- Python Type to PSQL Type Mapping (Helper) ---
# This helps the `literal` builder function infer the correct PsqlType class
PYTHON_TO_PSQL_TYPE_MAP = {
    bool: PsqlBool,
    int: PsqlInt,  # Default to INTEGER for int, use specific builder if SMALLINT/BIGINT needed
    float: PsqlDoublePrecision,  # Default to double precision
    str: PsqlVarChar,  # Default to VARCHAR
    date: PsqlDate,
    time: PsqlTime,
    datetime: PsqlTimestamp,
    UUID: PsqlUuid,
    bytes: PsqlBytea,
    # List mapping needs explicit target type from user
}


# --- Python-level Casting Function ---
def py_cast(sql_value_obj: PsqlType, target_sql_type_class: type[PsqlType]) -> PsqlType:
    """
    Attempts to convert a Python value held by one PsqlType object
    into another PsqlType object. Performs validation.
    This does *NOT* generate PSQL CAST functions.
    """
    # Simplistic example: try creating the target type with the source value
    # More sophisticated logic might be needed for some conversions (e.g., int -> str)
    try:
        # Extract the raw Python value and try to create the target type
        return target_sql_type_class(sql_value_obj.value)
    except (PsqlValueError, PsqlTypeError) as e:
        raise PsqlTypeError(
            f"Cannot cast {sql_value_obj!r} "
            f"(type {type(sql_value_obj).__name__}) to "
            f"{target_sql_type_class.__name__}: {e}"
        ) from e
    except Exception as e:  # Catch unexpected errors during conversion
        raise PsqlTypeError(
            f"Unexpected error casting {sql_value_obj!r} to "
            f"{target_sql_type_class.__name__}: {e}"
        ) from e
