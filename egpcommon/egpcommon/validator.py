"""Validator base class for EGP."""

from datetime import UTC, datetime
from ipaddress import ip_address
from os.path import normpath, splitext
from re import IGNORECASE, Pattern
from re import compile as regex_compile
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse, urlunparse
from uuid import UUID

from egpcommon.common import _RESERVED_FILE_NAMES, EGP_EPOCH
from egpcommon.egp_log import VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class Validator:
    """Validate data.

    The class provides a set of functions to validate data. Validation typically is done
    by checking that a value is of a certain type, within a certain range, or matches a
    certain pattern. The class provides a set of functions to validate these conditions.

    All validation functions return a boolean value if the _logger.isEnabledFor(level=VERIFY)
    is False or if the validation passes (in which case True is returned).

    The naming convention for the validation functions is _is_<condition> or _in_<set>. The
    functions all take the following parameters (though more are not prohibited):
    - attr: The name of the attribute being validated.
    - value: The value of the attribute being validated.

    If a check fails a log message will be produced at level VERIFY and include the attribute
    name, the expected condition and the actual value. This log message shall be wrapped in an
    if _logger.isEnabledFor(level=VERIFY) check to avoid the overhead of string formatting
    when the log level is higher than VERIFY and permit dynamic evaluation of log levels.

    Validator is usually inherited with DictTypeAccessor to provide a simple get/set dictionary
    like access to an object's members with validation.
    """

    __slots__ = tuple()

    # Designed to match strings that meet the following criteria:
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

    def _in_range(self, attr: str, value: int | float, minm: float, maxm: float) -> bool:
        """Check if the value is in a range."""
        result = value >= minm and value <= maxm
        if not result:
            _logger.log(VERIFY, "%s must be between %s and %s but is %s", attr, minm, maxm, value)
        return result

    def _is_accessible(self, attr: str, value: Any) -> bool:
        """Check if the value is a path to a file that can be read."""
        if not self._is_path(attr, value):
            return False
        value = normpath(value)
        try:
            with open(value, "r", encoding="utf-8"):
                pass
        except FileNotFoundError:
            if _logger.isEnabledFor(VERIFY):
                _logger.log(
                    VERIFY,
                    "%s must be a path to a file that can be read: %s does not exist.",
                    attr,
                    value,
                )
            return False
        except PermissionError:
            if _logger.isEnabledFor(VERIFY):
                _logger.log(
                    VERIFY,
                    "%s must be a path to a file that can be read: %s is not accessible.",
                    attr,
                    value,
                )
            return False
        return True

    def _is_bool(self, attr: str, value: Any) -> bool:
        """Check if the value is a bool."""
        result = isinstance(value, bool)
        if not result:
            _logger.log(VERIFY, "%s must be a bool but is %s", attr, type(value))
        return result

    def _is_bytes(self, attr: str, value: Any) -> bool:
        """Check if the value is bytes."""
        result = isinstance(value, bytes)
        if not result:
            _logger.log(VERIFY, "%s must be bytes but is %s", attr, type(value))
        return result

    def _is_callable(self, attr: str, value: Any) -> bool:
        """Check if the value is callable."""
        result = callable(value)
        if not result:
            _logger.log(VERIFY, "%s must be callable but is %s", attr, type(value))
        return result

    def _is_datetime(self, attr: str, value: Any) -> bool:
        """Check if the value is a datetime."""
        result = isinstance(value, datetime)
        if not result:
            _logger.log(VERIFY, "%s must be a datetime but is %s", attr, type(value))
        return result

    def _is_dict(self, attr: str, value: Any) -> bool:
        """Check if the value is a dict."""
        result = isinstance(value, dict)
        if not result:
            _logger.log(VERIFY, "%s must be a dict but is %s", attr, type(value))
        return result

    def _is_filename(self, attr: str, value: str) -> bool:
        """Validate a filename without any preceding path."""
        if not self._is_string(attr, value):
            return False
        if not self._is_length(attr, value, 1, 256):
            return False
        if self._is_regex(attr, value, self._illegal_filename_regex):
            if _logger.isEnabledFor(VERIFY):
                _logger.log(
                    VERIFY,
                    "%s must be a valid filename without a preceding path: %s is not valid.",
                    attr,
                    value,
                )
            return False
        if value.upper() in _RESERVED_FILE_NAMES:
            name, ext = splitext(value)
            if not ((name.upper() in _RESERVED_FILE_NAMES) and len(ext) > 0):
                if _logger.isEnabledFor(VERIFY):
                    _logger.log(
                        VERIFY,
                        "%s not include a reserved name (%s): %s is not valid.",
                        attr,
                        _RESERVED_FILE_NAMES,
                        value,
                    )
                return False
        return True

    def _is_float(self, attr: str, value: Any) -> bool:
        """Check if the value is a float."""
        result = isinstance(value, float)
        if not result:
            _logger.log(VERIFY, "%s must be a float but is %s", attr, type(value))
        return result

    def _is_hash8(self, attr: str, value: Any, _assert: bool = True) -> bool:
        """Check if the value is a hash8."""
        result = self._is_bytes(attr, value) and len(value) == 8
        if not result:
            _logger.log(VERIFY, "%s must be a hash8 but is %s", attr, value)
        return result

    def _is_historical_datetime(self, attr: str, value: Any) -> bool:
        """Check if the value is a historical datetime."""
        if not self._is_datetime(attr, value):
            return False
        result = EGP_EPOCH <= value <= datetime.now(UTC)
        if not result:
            _logger.log(
                VERIFY, "%s must be a post-EGP epoch historical datetime but is %s", attr, value
            )
        return result

    def _is_hostname(self, attr: str, value: str) -> bool:
        """Validate a hostname."""
        if len(value) > 255:
            if _logger.isEnabledFor(VERIFY):
                _logger.log(VERIFY, "%s must be a valid hostname: %s is >255 chars.", attr, value)
            return False
        if len(value) > 1 and value[-1] == ".":
            value = value[:-1]  # Strip exactly one dot from the right, if present
        result = all(self._hostname_regex.match(x) for x in value.split("."))
        if not result:
            _logger.log(VERIFY, "%s must be a valid hostname: %s is not valid.", attr, value)
        return result

    def _is_instance(self, attr: str, value: Any, cls: type | tuple[type, ...]) -> bool:
        """Check if the value is an instance of a class."""
        result = isinstance(value, cls)
        if not result:
            _logger.log(VERIFY, "%s must be an instance of %s but is %s", attr, cls, type(value))
        return result

    def _is_int(self, attr: str, value: Any) -> bool:
        """Check if the value is an int."""
        result = isinstance(value, int)
        if not result:
            _logger.log(VERIFY, "%s must be an int but is %s", attr, type(value))
        return result

    def _is_ip(self, attr: str, value: str) -> bool:
        """Validate an IP address (both IPv4 and IPv6)."""
        try:
            ip_address(value)
            return True
        except ValueError:
            if _logger.isEnabledFor(VERIFY):
                _logger.log(VERIFY, "%s must be a valid IP address: %s is not valid.", attr, value)
        return False

    def _is_ip_or_hostname(self, attr: str, value: str) -> bool:
        """Validate an IP address or hostname."""
        result = self._is_ip(attr, value) or self._is_hostname(attr, value)
        if not result:
            _logger.log(
                VERIFY,
                "%s must be a valid IP address or hostname: %s is not valid.",
                attr,
                value,
            )
        return result

    def _is_length(self, attr: str, value: Any, minm: int, maxm: int) -> bool:
        """Check the length of the value."""
        result = len(value) >= minm and len(value) <= maxm
        if not result:
            _logger.log(
                VERIFY,
                "%s must be between %s and %s in length but is %s",
                attr,
                minm,
                maxm,
                len(value),
            )
        return result

    def _is_list(self, attr: str, value: Any) -> bool:
        """Check if the value is a list."""
        result = isinstance(value, list)
        if not result:
            _logger.log(VERIFY, "%s must be a list but is %s", attr, type(value))
        return result

    def _is_not_none(self, attr: str, value: Any) -> bool:
        """Check if the value is not None."""
        result = value is not None
        if not result:
            _logger.log(VERIFY, "%s must not be None", attr)
        return result

    def _is_one_of(self, attr: str, value: Any, values: Iterable[Any]) -> bool:
        """Check if the value is one of a set of values."""
        result = value in values
        if not result:
            _logger.log(VERIFY, "%s must be one of %s but is %s", attr, values, value)
        return result

    def _is_password(self, attr: str, value: str) -> bool:
        """Validate a password."""
        if not self._is_string(attr, value):
            return False
        return self._is_regex(attr, value, self._password_regex)

    def _is_path(self, attr: str, value: str) -> bool:
        """Validate a path."""
        return self._is_string(attr, value)

    def _is_printable_string(self, attr: str, value: str) -> bool:
        """Validate a printable string."""
        if not self._is_string(attr, value):
            return False
        result = value.isprintable()
        if not result:
            _logger.log(VERIFY, "%s must be a printable string but is not.", attr)
        return result

    def _is_regex(self, attr: str, value: str, pattern: Pattern) -> bool:
        """Check the value against a regex."""
        result = pattern.fullmatch(value)
        if not result:
            _logger.log(VERIFY, "%s must match the pattern %s but does not", attr, pattern)
        return bool(result)

    def _is_sequence(self, attr: str, value: Any) -> bool:
        """Check if the value is a sequence."""
        result = isinstance(value, Sequence)
        if not result:
            _logger.log(VERIFY, "%s must be a sequence but is %s", attr, type(value))
        return result

    def _is_sha256(self, attr: str, value: Any) -> bool:
        """Check if the value is a SHA256 hash."""
        result = self._is_bytes(attr, value) and len(value) == 32
        if not result:
            _logger.log(VERIFY, "%s must be a SHA256 hash but is %s", attr, value)
        return result

    def _is_simple_string(self, attr: str, value: str) -> bool:
        """Validate a simple string."""
        if not self._is_string(attr, value):
            return False
        return self._is_regex(attr, value, self._simple_string_regex)

    def _is_string(self, attr: str, value: Any) -> bool:
        """Check if the value is a string."""
        result = isinstance(value, str)
        if not result:
            _logger.log(VERIFY, "%s must be a string but is %s", attr, type(value))
        return result

    def _is_tuple(self, attr: str, value: Any) -> bool:
        """Check if the value is a tuple."""
        result = isinstance(value, tuple)
        if not result:
            _logger.log(VERIFY, "%s must be a tuple but is %s", attr, type(value))
        return result

    def _is_url(self, attr: str, value: str) -> bool:
        """Validate a URL."""
        if not self._is_string(attr, value):
            return False
        if not self._is_regex(attr, value, self._url_regex):
            return False
        presult = urlparse(value)
        # Ensure the scheme is HTTPS and the network location is present
        if presult.scheme != "https" or not presult.netloc:
            _logger.log(VERIFY, "%s must be a valid URL: %s is not valid.", attr, value)
            return False

        # Rebuild the URL to ensure it is properly formed
        reconstructed_url = urlunparse(presult)
        if reconstructed_url != value:
            _logger.log(VERIFY, "%s must be a valid URL: %s is not valid.", attr, value)
            return False
        return True

    def _is_uuid(self, attr: str, value: Any) -> bool:
        """Check if the value is a UUID."""
        result = isinstance(value, UUID)
        if not result:
            _logger.log(VERIFY, "%s must be a UUID but is %s", attr, type(value))
        return result
