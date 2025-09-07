"""The sql_types module defines the types for interacting with
a PostgreSQL database as a physical genetic code storage. This is the
role of the selectors."""

import datetime
import uuid
from abc import ABC, abstractmethod


# --- Custom Exceptions ---
class SqlValueError(ValueError):
    """Value is invalid for the specific SQL type."""

    pass


class SqlTypeError(TypeError):
    """Type mismatch during SQL expression construction."""

    pass


# --- Base SQL Type ---
class SqlType(ABC):
    """Abstract base class for SQL type representations."""

    # Using __slots__ for potentially many instances created during GP
    __slots__ = ("value",)

    # Class variable holding the standard SQL type name
    sql_type_name: str = "SqlType"  # Override in subclasses

    def __init__(self, value):
        self.value = self._validate(value)

    @abstractmethod
    def _validate(self, value):
        """Validate the Python value against SQL type constraints.
        Return the validated (possibly type-converted) value or raise SqlValueError.
        """
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    def __eq__(self, other):
        # Basic equality for potential use in GP state
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    # Potentially add __hash__ if needed, ensuring immutability


class SqlNumber(SqlType):
    """Base class for numeric SQL types."""

    pass


class SqlIntegral(SqlNumber):
    """Base class for integral SQL types."""

    pass


class SqlNumeric(SqlNumber):
    """Base class for numeric SQL types that are not integral."""

    pass


# --- Concrete SQL Types ---
class SqlBool(SqlType):
    """Boolean type."""

    sql_type_name = "BOOL"

    def _validate(self, value):
        if not isinstance(value, bool):
            # Allow 0/1? GP might generate ints. Let's be strict for now.
            raise SqlValueError(f"Invalid value for BOOL: {value!r}. Must be True or False.")
        return value


class SqlSmallInt(SqlIntegral):
    """Small integer type (16 bits)"""

    sql_type_name = "INT2"
    MIN_VALUE = -32768
    MAX_VALUE = 32767

    def _validate(self, value):
        if not isinstance(value, int):
            raise SqlValueError(f"Invalid type for SMALLINT: {type(value).__name__}. Must be int.")
        if not self.MIN_VALUE <= value <= self.MAX_VALUE:
            raise SqlValueError(
                f"Value {value} out of range for SMALLINT ({self.MIN_VALUE} to {self.MAX_VALUE})."
            )
        return value


class SqlInt(SqlIntegral):
    """Integer type (32 bits)"""

    sql_type_name = "INT4"
    MIN_VALUE = -2147483648
    MAX_VALUE = 2147483647

    def _validate(self, value):
        if not isinstance(value, int):
            raise SqlValueError(f"Invalid type for INTEGER: {type(value).__name__}. Must be int.")
        if not self.MIN_VALUE <= value <= self.MAX_VALUE:
            raise SqlValueError(
                f"Value {value} out of range for INTEGER ({self.MIN_VALUE} to {self.MAX_VALUE})."
            )
        return value


class SqlBigInt(SqlIntegral):
    """Big integer type (64 bits)"""

    sql_type_name = "BIGINT"
    MIN_VALUE = -9223372036854775808
    MAX_VALUE = 9223372036854775807

    def _validate(self, value):
        if not isinstance(value, int):
            raise SqlValueError(f"Invalid type for BIGINT: {type(value).__name__}. Must be int.")
        if not self.MIN_VALUE <= value <= self.MAX_VALUE:
            raise SqlValueError(
                f"Value {value} out of range for BIGINT ({self.MIN_VALUE} to {self.MAX_VALUE})."
            )
        return value


class SqlReal(SqlNumeric):
    """Single precision floating point type (32 bits)"""

    sql_type_name = "REAL"

    def _validate(self, value):
        if not isinstance(value, (float, int)):  # Allow ints to become floats
            raise SqlValueError(
                f"Invalid type for REAL: {type(value).__name__}. Must be float or int."
            )
        return float(value)  # Store as float


class SqlDoublePrecision(SqlNumeric):
    """Double precision floating point type (64 bits)"""

    sql_type_name = "DOUBLE PRECISION"

    def _validate(self, value):
        if not isinstance(value, (float, int)):
            raise SqlValueError(
                f"Invalid type for DOUBLE PRECISION: {type(value).__name__}. Must be float or int."
            )
        return float(value)


class SqlChar(SqlType):
    """Character type (fixed length)"""

    sql_type_name = "CHAR"  # Note: CHAR has fixed length semantics in SQL

    # Add length validation if needed, passed to __init__?
    def __init__(self, value, length=None):  # Example if length needed
        self.length = length
        super().__init__(value)

    def _validate(self, value):
        if not isinstance(value, str):
            raise SqlValueError(f"Invalid type for CHAR: {type(value).__name__}. Must be str.")
        # Optional: Add length check if self.length is set
        # if self.length is not None and len(value) > self.length:
        #    raise SqlValueError(f"Value '{value}' too long for CHAR({self.length}).")
        return value


class SqlVarChar(SqlType):
    """Variable character type (length is not fixed)"""

    sql_type_name = "VARCHAR"

    # Add length validation if needed
    def __init__(self, value, length=None):  # Example if length needed
        self.length = length
        super().__init__(value)

    def _validate(self, value):
        if not isinstance(value, str):
            raise SqlValueError(f"Invalid type for VARCHAR: {type(value).__name__}. Must be str.")
        # Optional: Add length check if self.length is set
        # if self.length is not None and len(value) > self.length:
        #    raise SqlValueError(f"Value '{value}' too long for VARCHAR({self.length}).")
        return value


class SqlDate(SqlType):
    """Date type (no time)"""

    sql_type_name = "DATE"

    def _validate(self, value):
        if not isinstance(value, datetime.date):
            # Allow datetime objects? Truncate? Be strict for now.
            raise SqlValueError(
                f"Invalid type for DATE: {type(value).__name__}. Must be datetime.date."
            )
        return value


class SqlTime(SqlType):
    """Time type (no date)"""

    sql_type_name = "TIME"

    def _validate(self, value):
        if not isinstance(value, datetime.time):
            raise SqlValueError(
                f"Invalid type for TIME: {type(value).__name__}. Must be datetime.time."
            )
        return value


class SqlTimestamp(SqlType):
    """Timestamp type (date and time)"""

    sql_type_name = "TIMESTAMP"  # Assumes 'timestamp without time zone'

    def _validate(self, value):
        if not isinstance(value, datetime.datetime):
            raise SqlValueError(
                f"Invalid type for TIMESTAMP: {type(value).__name__}. Must be datetime.datetime."
            )
        return value


class SqlUuid(SqlType):
    """UUID type"""

    sql_type_name = "UUID"

    def _validate(self, value):
        if not isinstance(value, uuid.UUID):
            raise SqlValueError(
                f"Invalid type for UUID: {type(value).__name__}. Must be uuid.UUID."
            )
        return value


class SqlBytea(SqlType):
    """Binary data type"""

    sql_type_name = "BYTEA"

    def _validate(self, value):
        if not isinstance(value, bytes):
            raise SqlValueError(f"Invalid type for BYTEA: {type(value).__name__}. Must be bytes.")
        return value


# --- Array Types ---
class SqlArray(SqlType):
    """Base for array types."""

    sql_type_name = "ARRAY"  # Needs element type
    element_type: type[SqlType]  # Defined in subclasses

    def _validate(self, value):
        if not isinstance(value, list):
            raise SqlValueError(
                f"Invalid type for {self.sql_type_name}: {type(value).__name__}. Must be list."
            )
        # Validate each element using the specific element type's validator
        validated_elements = []
        for i, item in enumerate(value):
            try:
                # Create an instance of the element type to trigger its validation
                validated_element = self.element_type(item).value
                validated_elements.append(validated_element)
            except SqlValueError as e:
                raise SqlValueError(
                    f"Invalid element at index {i} for {self.sql_type_name}: {e}"
                ) from e
        return validated_elements

    @classmethod
    def get_sql_type_name(cls):
        """Get the full SQL type name including element type."""
        # Produces e.g., "INT4[]"
        return f"{cls.element_type.sql_type_name}[]"


# Concrete Array examples (Integer types, Float types, Char types)
class SqlBoolArray(SqlArray):
    """Boolean array type (1 bit)"""

    element_type = SqlBool
    sql_type_name = element_type.sql_type_name + "[]"


class SqlIntArray(SqlArray):
    """Integer array type (32 bits)"""

    element_type = SqlInt
    sql_type_name = element_type.sql_type_name + "[]"


class SqlSmallIntArray(SqlArray):
    """Small integer array type (16 bits)"""

    element_type = SqlSmallInt
    sql_type_name = element_type.sql_type_name + "[]"


class SqlBigIntArray(SqlArray):
    """Big integer array type (64 bits)"""

    element_type = SqlBigInt
    sql_type_name = element_type.sql_type_name + "[]"


class SqlRealArray(SqlArray):
    """Single precision floating point array type (32 bits)"""

    element_type = SqlReal
    sql_type_name = element_type.sql_type_name + "[]"


class SqlDoublePrecisionArray(SqlArray):
    """Double precision floating point array type (64 bits)"""

    element_type = SqlDoublePrecision
    sql_type_name = element_type.sql_type_name + "[]"


# --- Python Type to SQL Type Mapping (Helper) ---
# This helps the `literal` builder function infer the correct SqlType class
PYTHON_TO_SQL_TYPE_MAP = {
    bool: SqlBool,
    int: SqlInt,  # Default to INTEGER for int, use specific builder if SMALLINT/BIGINT needed
    float: SqlDoublePrecision,  # Default to double precision
    str: SqlVarChar,  # Default to VARCHAR
    datetime.date: SqlDate,
    datetime.time: SqlTime,
    datetime.datetime: SqlTimestamp,
    uuid.UUID: SqlUuid,
    bytes: SqlBytea,
    # List mapping needs explicit target type from user
}


# --- Python-level Casting Function ---
def py_cast(sql_value_obj: SqlType, target_sql_type_class: type[SqlType]) -> SqlType:
    """
    Attempts to convert a Python value held by one SqlType object
    into another SqlType object. Performs validation.
    This does *NOT* generate SQL CAST functions.
    """
    # Simplistic example: try creating the target type with the source value
    # More sophisticated logic might be needed for some conversions (e.g., int -> str)
    try:
        # Extract the raw Python value and try to create the target type
        return target_sql_type_class(sql_value_obj.value)
    except (SqlValueError, SqlTypeError) as e:
        raise SqlTypeError(
            f"Cannot cast {sql_value_obj!r} "
            f"(type {type(sql_value_obj).__name__}) to "
            f"{target_sql_type_class.__name__}: {e}"
        ) from e
    except Exception as e:  # Catch unexpected errors during conversion
        raise SqlTypeError(
            f"Unexpected error casting {sql_value_obj!r} to "
            f"{target_sql_type_class.__name__}: {e}"
        ) from e
