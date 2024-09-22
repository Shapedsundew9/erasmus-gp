"""Common functions for the EGPPY package."""

from typing import Any, Self
from copy import deepcopy
from datetime import UTC, datetime
from re import Pattern, IGNORECASE
from re import compile as regex_compile
from ipaddress import ip_address
from os.path import normpath, split, splitext
from urllib.parse import urlparse, urlunparse
from uuid import UUID


# When  it all began...
EGP_EPOCH = datetime(year=2019, month=12, day=25, hour=16, minute=26, second=0, tzinfo=UTC)


# Constants
NULL_SHA256: bytes = b"\x00" * 32
NULL_SHA256_STR = NULL_SHA256.hex()
NULL_UUID: UUID = UUID(int=0)


# Local Constants
_RESERVED_FILE_NAMES: set[str] = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


# https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
def merge(  # pylint: disable=dangerous-default-value
    dict_a: dict[Any, Any],
    dict_b: dict[Any, Any],
    path: list[str] = [],
    no_new_keys: bool = False,
    update=False,
) -> dict[Any, Any]:
    """Merge dict b into a recursively. a is modified.
    This function is equivilent to a.update(b) unless update is False in which case
    if b contains dictionary differing values with the same key a ValueError is raised.
    If there are dictionaries
    in b that have the same key as a then those dictionaries are merged in the same way.
    Keys in a & b (or common key'd sub-dictionaries) where one is a dict and the other
    some other type raise an exception.

    Args
    ----
    a: Dictionary to merge in to.
    b: Dictionary to merge.
    no_new_keys: If True keys in b that are not in a are ignored
    update: When false keys with non-dict values that differ will raise an error.

    Returns
    -------
    a (modified)
    """
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                merge(dict_a[key], dict_b[key], path + [str(key)], no_new_keys, update)
            elif dict_a[key] == dict_b[key]:
                pass  # same leaf value
            elif not update:
                raise ValueError(f"Conflict at {'.'.join(path + [str(key)])}")
            else:
                dict_a[key] = dict_b[key]
        elif not no_new_keys:
            dict_a[key] = dict_b[key]
    return dict_a


class DictTypeAccessor:
    """Provide very simple get/set dictionary like access to an objects members."""

    def __getitem__(self, key: str) -> Any:
        """Get the value of the attribute."""
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the value of the attribute."""
        setattr(self, key, value)

    def copy(self) -> Self:
        """Return a dictionary of the object."""
        return deepcopy(self)

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of the attribute."""
        return getattr(self, key, default)

    def setdefault(self, key: str, default: Any) -> Any:
        """Get the value of the attribute."""
        if hasattr(self, key):
            return getattr(self, key)
        setattr(self, key, default)
        return default


class Validator:
    """Validate data.

    The class provides a set of functions to validate data. Validation typically is done
    by asserting that a value is of a certain type, within a certain range, or matches a
    certain pattern. The class provides a set of functions to validate these conditions.

    All validation functions return a boolean value if the parameter _assert is False. If
    _assert is True, the function will raise an AssertionError if the condition is not met.

    The naming convention for the validation functions is _is_<condition> or _in_<set>. The
    functions all take the following parameters (though more are not prohibited):
    - attr: The name of the attribute being validated.
    - value: The value of the attribute being validated.
    - _assert: If True, the function will raise an AssertionError if the conditions are not met.
    """

    _hostname_regex_str: str = r"^(?!-)[A-Z\d-]{1,63}(?<!-)$"
    _hostname_regex: Pattern = regex_compile(_hostname_regex_str, IGNORECASE)

    # Designed to match strings that meet the following criteria:
    #   At least one lowercase letter ([a-z]).
    #   At least one uppercase letter ([A-Z]).
    #   At least one digit (\d).
    #   At least one special character ([\W_]), where \W matches any non-word character, including
    #   punctuation and space, and _ is explicitly included.
    #   The total length of the string must be between 8 and 32 characters.
    _password_regex_str: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,32}$"
    _password_regex: Pattern = regex_compile(_password_regex_str)
    _simple_string_regex_str: str = r"^[a-zA-Z0-9_-]+$"
    _simple_string_regex: Pattern = regex_compile(_simple_string_regex_str)
    _printable_string_regex_str: str = r"^[ -~]+$"
    _printable_string_regex: Pattern = regex_compile(_printable_string_regex_str)
    _illegal_filename_regex_str: str = r'[<>:"/\\|?*]'
    _illegal_filename_regex: Pattern = regex_compile(_illegal_filename_regex_str)

    # URL regex
    _url_regex_str: str = (
        r"^(https?|ftp):\/\/"  # http, https, or ftp protocol
        r"(\w+(\-\w+)*\.)+[a-z]{2,}"  # domain name
        r"(\/[\w\-\/]*)*"  # resource path
        r"(\?\w+=\w+(&\w+=\w+)*)?"  # query parameters
        r"(#\w*)?$"  # fragment identifier
    )
    _url_regex: Pattern = regex_compile(_url_regex_str, IGNORECASE)

    def consistency(self) -> None:
        """Check the consistency of the object."""

    def _in_range(
        self, attr: str, value: int | float, minm: float, maxm: float, _assert: bool = True
    ) -> bool:
        """Check if the value is in a range."""
        result = value >= minm and value <= maxm
        if _assert:
            assert result, f"{attr} must be between {minm} and {maxm} but is {value}"
        return result

    def _is_bool(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a bool."""
        result = isinstance(value, bool)
        if _assert:
            assert result, f"{attr} must be a bool but is {type(value)}"
        return result

    def _is_bytes(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is bytes."""
        result = isinstance(value, bytes)
        if _assert:
            assert result, f"{attr} must be bytes but is {type(value)}"
        return result

    def _is_callable(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is callable."""
        result = callable(value)
        if _assert:
            assert result, f"{attr} must be callable but is {type(value)}"
        return result

    def _is_datetime(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a datetime."""
        result = isinstance(value, datetime)
        if _assert:
            assert result, f"{attr} must be a datetime but is {type(value)}"
        return result

    def _is_dict(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a dict."""
        result = isinstance(value, dict)
        if _assert:
            assert result, f"{attr} must be a dict but is {type(value)}"
        return result

    def _is_filename(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a filename without any preceding path."""
        result = self._is_string(attr, value, _assert)
        result = result and self._is_length(attr, value, 1, 256, _assert)
        result = result and not self._is_regex(attr, value, self._illegal_filename_regex, False)
        if _assert:
            assert result, (
                f"{attr} must be a valid filename without a "
                f"preceding path: {value} is not valid."
            )
        result = result and value.upper() in _RESERVED_FILE_NAMES
        name, ext = splitext(value)
        result = result or ((name.upper() in _RESERVED_FILE_NAMES) and len(ext) > 0)
        if _assert:
            assert result, (
                f"{attr} not include a reserved name"
                f" ({_RESERVED_FILE_NAMES}): {value} is not valid."
            )
        return result

    def _is_float(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a float."""
        result = isinstance(value, float)
        if _assert:
            assert result, f"{attr} must be a float but is {type(value)}"
        return result

    def _is_hash8(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a hash8."""
        result = self._is_bytes(attr, value, False) and len(value) == 8
        if _assert:
            assert result, f"{attr} must be a hash8 but is {value}"
        return result

    def _is_historical_datetime(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a historical datetime."""
        result = self._is_datetime(attr, value, _assert)
        result = result or (value >= EGP_EPOCH and value <= datetime.now(UTC))
        if _assert:
            assert result, f"{attr} must be a post-EGP epoch historical datetime but is {value}"
        return result

    def _is_hostname(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a hostname."""
        if len(value) > 255:
            assert not _assert, f"{attr} must be a valid hostname: {value} is >255 chars."
            return False
        if value[-1] == ".":
            value = value[:-1]  # Strip exactly one dot from the right, if present
        result = all(self._hostname_regex.match(x) for x in value.split("."))
        if _assert:
            assert result, f"{attr} must be a valid hostname: {value} is not valid."
        return result

    def _is_instance(
        self, attr: str, value: Any, cls: type | tuple[type, ...], _assert: bool = True
    ) -> bool:
        """Check if the value is an instance of a class."""
        result = isinstance(value, cls)
        if _assert:
            assert result, f"{attr} must be an instance of {cls} but is {type(value)}"
        return result

    def _is_int(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is an int."""
        result = isinstance(value, int)
        if _assert:
            assert result, f"{attr} must be an int but is {type(value)}"
        return result

    def _is_ip(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate an IP address (both IPv4 and IPv6)."""
        try:
            ip_address(value)
        except ValueError:
            assert not _assert, f"{attr} must be a valid IP address: {value} is not valid."
            return False
        return True

    def _is_ip_or_hostname(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate an IP address or hostname."""
        result = self._is_ip(attr, value, False) or self._is_hostname(attr, value, False)
        if _assert:
            assert result, f"{attr} must be a valid IP address or hostname: {value} is not valid."
        return result

    def _is_list(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a list."""
        result = isinstance(value, list)
        if _assert:
            assert result, f"{attr} must be a list but is {type(value)}"
        return result

    def _is_not_none(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is not None."""
        result = value is not None
        if _assert:
            assert result, f"{attr} must not be None"
        return result

    def _is_one_of(
        self, attr: str, value: Any, values: tuple[Any, ...], _assert: bool = True
    ) -> bool:
        """Check if the value is one of a set of values."""
        result = value in values
        if _assert:
            assert result, f"{attr} must be one of {values} but is {value}"
        return result

    def _is_password(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a password."""
        result = self._is_string(attr, value, _assert)
        result = result and self._is_regex(attr, value, self._password_regex, _assert)
        return result

    def _is_path(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a path."""
        result = self._is_string(attr, value, _assert)
        normalized_path = normpath(value)
        head, tail = split(normalized_path)
        if _assert:
            assert head and not tail, (
                f"{attr} must be a valid folder path without a filename: " f" {value} is not valid."
            )
        return result

    def _is_printable_string(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a printable string."""
        result = self._is_string(attr, value, _assert)
        result = result and self._is_regex(attr, value, self._printable_string_regex, _assert)
        return result

    def _is_sha256(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a SHA256 hash."""
        result = self._is_bytes(attr, value, False) and len(value) == 32
        if _assert:
            assert result, f"{attr} must be a SHA256 hash but is {value}"
        return result

    def _is_simple_string(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a simple string."""
        result = self._is_string(attr, value, False)
        result = result and self._is_regex(attr, value, self._simple_string_regex, _assert)
        return result

    def _is_string(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a string."""
        result = isinstance(value, str)
        if _assert:
            assert result, f"{attr} must be a string but is {type(value)}"
        return result

    def _is_tuple(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a tuple."""
        result = isinstance(value, tuple)
        if _assert:
            assert result, f"{attr} must be a tuple but is {type(value)}"
        return result

    def _is_url(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a URL."""
        result = self._is_string(attr, value, False)
        result = result and self._is_regex(attr, value, self._url_regex, _assert)
        presult = urlparse(value)
        # Ensure the scheme is HTTPS and the network location is present
        if presult.scheme != "https" or not presult.netloc:
            if _assert:
                assert False, f"{attr} must be a valid URL: {value} is not valid."
            return False

        # Rebuild the URL to ensure it is properly formed
        reconstructed_url = urlunparse(presult)
        if reconstructed_url != value and _assert:
            assert False, f"{attr} must be a valid URL: {value} is not valid."
        return result

    def _is_uuid(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a UUID."""
        result = isinstance(value, UUID)
        if _assert:
            assert result, f"{attr} must be a UUID but is {type(value)}"
        return result

    def _is_length(self, attr: str, value: Any, minm: int, maxm: int, _assert: bool = True) -> bool:
        """Check the length of the value."""
        result = len(value) >= minm and len(value) <= maxm
        if _assert:
            assert result, f"{attr} must be between {minm} and {maxm} in length but is {len(value)}"
        return result

    def _is_regex(self, attr: str, value: str, pattern: Pattern, _assert: bool = True) -> bool:
        """Check the value against a regex."""
        result = pattern.fullmatch(value)
        if _assert:
            assert result, f"{attr} must match the pattern {pattern} but does not"
        return bool(result)
