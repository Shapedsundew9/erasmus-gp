"""The psql_types module defines the types for interacting with
a PostgreSQL database as a physical genetic code storage. This is the
role of the selectors."""

from abc import ABC, abstractmethod
from datetime import date, datetime, time
from itertools import count
from typing import Any
from uuid import UUID

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

    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlType with a value.

        If both is_literal and is_column are False then the value is treated as an expression.

        Args:
            value:      The Python variable value to use as a literal or the
                        column name as a string.
            is_literal: If True, 'value' is treated as a literal value
            is_column:  If True, 'value' is treated as a column name
            uid:        Unique ID for the literal, assigned automatically if -1 and is_literal
                        is True (the default). Typically hard codong the UID is only used for
                        testing

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
        self.uid: int = next(self.counter) if is_literal and uid == -1 else uid

    def __eq__(self, other):
        """Compare two PsqlType objects for equality.

        Args:
            other: The object to compare with.

        Returns:
            True if the objects are of the same class and their values are equal,
            NotImplemented otherwise.
        """
        # Basic equality for potential use in GP state
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.value == other.value

    def __repr__(self):
        """Return a string representation of the PsqlType object.

        Returns:
            A string that can be used to recreate the object.
        """
        return f"{self.__class__.__name__}({self.value!r})"

    def __str__(self):
        """String representation for embedding in EGPDB Table PSQL expressions.
        The string returned is an f-string for easy embedding in PSQL expressions
        using a map to populate the column name or literal values.

        e.g. "{literal0} + {literal1} * {column_name}"
        """
        if self.is_column:
            assert isinstance(
                self.value, str
            ), "Internal error: PsqlType column value must be a string."
            # Write the column name in bracers as per EGPDB convention
            return f"{{{self.value}}}"
        if self.is_literal:
            return f"{{literal{self.uid}}}"
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
        """Validate the Python value for a PSQL BOOL.

        Args:
            value: The value to validate.

        Returns:
            The validated boolean value.

        Raises:
            PsqlValueError: If the value is not a boolean.
        """
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
        """Validate the Python value for a PSQL SMALLINT.

        Args:
            value: The value to validate.

        Returns:
            The validated integer value.

        Raises:
            PsqlValueError: If the value is not an int or is out of range.
        """
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
        """Validate the Python value for a PSQL INTEGER.

        Args:
            value: The value to validate.

        Returns:
            The validated integer value.

        Raises:
            PsqlValueError: If the value is not an int or is out of range.
        """
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
        """Validate the Python value for a PSQL BIGINT.

        Args:
            value: The value to validate.

        Returns:
            The validated integer value.

        Raises:
            PsqlValueError: If the value is not an int or is out of range.
        """
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
        """Validate the Python value for a PSQL REAL.

        Args:
            value: The value to validate.

        Returns:
            The validated float value.

        Raises:
            PsqlValueError: If the value is not a float or int.
        """
        if not isinstance(value, (float, int)):  # Allow ints to become floats
            raise PsqlValueError(
                f"Invalid type for REAL: {type(value).__name__}. Must be float or int."
            )
        return float(value)  # Store as float


class PsqlDoublePrecision(PsqlNumeric):
    """Double precision floating point type (64 bits)"""

    sql_type_name = "DOUBLE PRECISION"

    def _validate(self, value):
        """Validate the Python value for a PSQL DOUBLE PRECISION.

        Args:
            value: The value to validate.

        Returns:
            The validated float value.

        Raises:
            PsqlValueError: If the value is not a float or int.
        """
        if not isinstance(value, (float, int)):
            raise PsqlValueError(
                f"Invalid type for DOUBLE PRECISION: {type(value).__name__}. Must be float or int."
            )
        return float(value)


class PsqlChar(PsqlType):
    """Character type (fixed length)"""

    sql_type_name = "CHAR"  # Note: CHAR has fixed length semantics in PSQL

    # Add length validation if needed, passed to __init__?
    def __init__(
        self,
        value: Any,
        is_literal: bool = False,
        is_column: bool = False,
        length: int | None = None,
    ):  # Example if length needed
        """Initialize the PsqlChar object.

        Args:
            value: The Python variable value to use as a literal or the
                   column name as a string.
            is_literal: If True, 'value' is treated as a literal value.
            is_column: If True, 'value' is treated as a column name.
            length: The fixed length of the character type.
        """
        self.length = length
        super().__init__(value, is_literal=is_literal, is_column=is_column)

    def _validate(self, value):
        """Validate the Python value for a PSQL CHAR.

        Args:
            value: The value to validate.

        Returns:
            The validated string value.

        Raises:
            PsqlValueError: If the value is not a string.
        """
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
    def __init__(
        self,
        value: Any,
        is_literal: bool = False,
        is_column: bool = False,
        length: int | None = None,
    ):  # Example if length needed
        """Initialize the PsqlVarChar object.

        Args:
            value: The Python variable value to use as a literal or the
                   column name as a string.
            is_literal: If True, 'value' is treated as a literal value.
            is_column: If True, 'value' is treated as a column name.
            length: The maximum length of the character type.
        """
        self.length = length
        super().__init__(value, is_literal=is_literal, is_column=is_column)

    def _validate(self, value):
        """Validate the Python value for a PSQL VARCHAR.

        Args:
            value: The value to validate.

        Returns:
            The validated string value.

        Raises:
            PsqlValueError: If the value is not a string.
        """
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
        """Validate the Python value for a PSQL DATE.

        Args:
            value: The value to validate.

        Returns:
            The validated date value.

        Raises:
            PsqlValueError: If the value is not a date object.
        """
        if not isinstance(value, date) or isinstance(value, datetime):
            # Allow datetime objects? Truncate? Be strict for now.
            raise PsqlValueError(
                f"Invalid type for DATE: {type(value).__name__}. Must be date  (not datetime)."
            )
        return value


class PsqlTime(PsqlType):
    """Time type (no date)"""

    sql_type_name = "TIME"

    def _validate(self, value):
        """Validate the Python value for a PSQL TIME.

        Args:
            value: The value to validate.

        Returns:
            The validated time value.

        Raises:
            PsqlValueError: If the value is not a time object.
        """
        if not isinstance(value, time):
            raise PsqlValueError(f"Invalid type for TIME: {type(value).__name__}. Must be time.")
        return value


class PsqlTimestamp(PsqlType):
    """Timestamp type (date and time)"""

    sql_type_name = "TIMESTAMP"  # Assumes 'timestamp without time zone'

    def _validate(self, value):
        """Validate the Python value for a PSQL TIMESTAMP.

        Args:
            value: The value to validate.

        Returns:
            The validated datetime value.

        Raises:
            PsqlValueError: If the value is not a datetime object.
        """
        if not isinstance(value, datetime):
            raise PsqlValueError(
                f"Invalid type for TIMESTAMP: {type(value).__name__}. Must be datetime"
            )
        return value


class PsqlUuid(PsqlType):
    """UUID type"""

    sql_type_name = "UUID"

    def _validate(self, value):
        """Validate the Python value for a PSQL UUID.

        Args:
            value: The value to validate.

        Returns:
            The validated UUID value.

        Raises:
            PsqlValueError: If the value is not a UUID object.
        """
        if not isinstance(value, UUID):
            raise PsqlValueError(f"Invalid type for UUID: {type(value).__name__}. Must be UUID.")
        return value


class PsqlBytea(PsqlType):
    """Binary data type"""

    sql_type_name = "BYTEA"

    def _validate(self, value):
        """Validate the Python value for a PSQL BYTEA.

        Args:
            value: The value to validate.

        Returns:
            The validated bytes value.

        Raises:
            PsqlValueError: If the value is not a bytes object.
        """
        if not isinstance(value, bytes):
            raise PsqlValueError(f"Invalid type for BYTEA: {type(value).__name__}. Must be bytes.")
        return value


# --- Array Types ---
class PsqlArray(PsqlType, ABC):
    """Base for array types."""

    sql_type_name = "ARRAY"  # Needs element type
    element_type: type[PsqlType]  # Defined in subclasses

    @abstractmethod
    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlArray object."""
        super().__init__(value, is_literal=is_literal, is_column=is_column, uid=uid)

    def _validate(self, value):
        """Validate the Python value for a PSQL ARRAY.

        Args:
            value: The value to validate.

        Returns:
            The validated list of elements.

        Raises:
            PsqlValueError: If the value is not a list or if any element is invalid.
        """
        if not isinstance(value, list):
            raise PsqlValueError(
                f"Invalid type for {self.sql_type_name}: {type(value).__name__}. Must be list."
            )
        # Validate each element using the specific element type's validator
        validated_elements = []
        for i, item in enumerate(value):
            try:
                # Create an instance of the element type to trigger its validation
                validated_element = self.element_type(item, is_literal=True)
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

    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlBoolArray object."""
        super().__init__(value, is_literal=is_literal, is_column=is_column, uid=uid)


class PsqlIntArray(PsqlArray):
    """Integer array type (32 bits)"""

    element_type = PsqlInt
    sql_type_name = element_type.sql_type_name + "[]"

    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlIntArray object."""
        super().__init__(value, is_literal=is_literal, is_column=is_column, uid=uid)


class PsqlSmallIntArray(PsqlArray):
    """Small integer array type (16 bits)"""

    element_type = PsqlSmallInt
    sql_type_name = element_type.sql_type_name + "[]"

    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlSmallIntArray object."""
        super().__init__(value, is_literal=is_literal, is_column=is_column, uid=uid)


class PsqlBigIntArray(PsqlArray):
    """Big integer array type (64 bits)"""

    element_type = PsqlBigInt
    sql_type_name = element_type.sql_type_name + "[]"

    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlBigIntArray object."""
        super().__init__(value, is_literal=is_literal, is_column=is_column, uid=uid)


class PsqlRealArray(PsqlArray):
    """Single precision floating point array type (32 bits)"""

    element_type = PsqlReal
    sql_type_name = element_type.sql_type_name + "[]"

    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlRealArray object."""
        super().__init__(value, is_literal=is_literal, is_column=is_column, uid=uid)


class PsqlDoublePrecisionArray(PsqlArray):
    """Double precision floating point array type (64 bits)"""

    element_type = PsqlDoublePrecision
    sql_type_name = element_type.sql_type_name + "[]"

    def __init__(
        self, value: Any, is_literal: bool = False, is_column: bool = False, uid: int = -1
    ):
        """Initialize the PsqlDoublePrecisionArray object."""
        super().__init__(value, is_literal=is_literal, is_column=is_column, uid=uid)


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

    Args:
        sql_value_obj: The PsqlType object to cast from.
        target_sql_type_class: The PsqlType class to cast to.

    Returns:
        A new PsqlType object of the target type.

    Raises:
        PsqlTypeError: If the cast is not possible.
    """
    # Simplistic example: try creating the target type with the source value
    # More sophisticated logic might be needed for some conversions (e.g., int -> str)
    try:
        # Extract the raw Python value and try to create the target type
        value = sql_value_obj.value
        if issubclass(target_sql_type_class, (PsqlVarChar, PsqlChar)):
            value = str(value)
        return target_sql_type_class(value, is_literal=True)
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


class PsqlStatement:
    """Base class for PSQL statements."""


class PsqlFragment:
    """Class for PSQL statement fragments."""


class PsqlFragmentWhere(PsqlFragment):
    """Class for PSQL WHERE clause fragments."""

    def __init__(self, condition: PsqlBool):
        if condition.is_literal:
            raise PsqlValueError("WHERE condition must be a column or an expression.")
        self.condition = condition

    def __str__(self):
        """Render the WHERE clause as a string."""
        return f"WHERE {self.condition}"


class PsqlFragmentOrderBy(PsqlFragment):
    """Class for PSQL ORDER BY clause fragments."""

    def __init__(self, column: PsqlType, ascending: bool = True):
        if not column.is_column:
            raise PsqlValueError("ORDER BY column must be a column.")
        self.column = column
        self.ascending = ascending

    def __str__(self):
        """Render the ORDER BY clause as a string."""
        order = "ASC" if self.ascending else "DESC"
        return f"ORDER BY {self.column} {order}"


class PsqlStatementSelect(PsqlStatement):
    """Class for PSQL SELECT statements.

    SELECT only ever returns the signature column
    """

    def __init__(self, where: PsqlFragmentWhere, order_by: PsqlFragmentOrderBy):
        super().__init__()
        self.where = where
        self.order_by = order_by

    def __str__(self):
        """Render the SELECT statement as a string."""
        return f"SELECT {{signature}} FROM {{table}} {self.where} {self.order_by} LIMIT {{limit}}"
