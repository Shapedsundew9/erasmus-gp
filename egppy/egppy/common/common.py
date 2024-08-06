"""Common functions for the EGPPY package."""
from datetime import UTC, datetime
from re import Pattern, IGNORECASE
from re import compile as regex_compile
from ipaddress import ip_address
from typing import Any
from uuid import UUID


# When  it all began...
EGP_EPOCH = datetime(year=2019, month=12, day=25, hour=16, minute=26, second=0, tzinfo=UTC)


# Constants
NULL_SHA256: bytes = b"\x00" * 32
NULL_SHA256_STR = NULL_SHA256.hex()
NULL_UUID: UUID = UUID(int=0)


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


class Validator():
    """Validate data."""

    _hostname_regex_str: str = r"^(?!-)[A-Z\d-]{1,63}(?<!-)$"
    _hostname_regex: Pattern = regex_compile(_hostname_regex_str, IGNORECASE)
    _password_regex_str: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,32}$"
    _password_regex: Pattern = regex_compile(_password_regex_str)


    def __getitem__(self, key: str) -> Any:
        """Get the item."""
        return getattr(self, '_' + key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the item."""
        return getattr(self, key)(value)

    def _in_range(
            self, attr: str,
            value: int | float,
            minm: float,
            maxm: float,
            _assert: bool = True
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

    def _is_float(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a float."""
        result = isinstance(value, float)
        if _assert:
            assert result, f"{attr} must be a float but is {type(value)}"
        return result

    def _is_hostname(self, attr: str, value: str, _assert: bool = True)-> bool:
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

    def _is_password(self, attr: str, value: str, _assert: bool = True) -> bool:
        """Validate a password."""
        result = self._is_string(attr, value, _assert)
        result = result or self._regex(attr, value, self._password_regex, _assert)
        return result

    def _is_string(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a string."""
        result = isinstance(value, str)
        if _assert:
            assert result, f"{attr} must be a string but is {type(value)}"
        return result

    def _length(self, attr: str, value: Any, minm: int, maxm: int, _assert: bool = True) -> bool:
        """Check the length of the value."""
        result = len(value) >= minm and len(value) <= maxm
        if _assert:
            assert result, f"{attr} must be between {minm} and {maxm} in length but is {len(value)}"
        return result

    def _regex(self, attr: str, value: str, pattern: Pattern, _assert: bool = True) -> bool:
        """Check the value against a regex."""
        result = pattern.fullmatch(value)
        if _assert:
            assert result, f"{attr} must match the pattern {pattern} but does not"
        return bool(result)
