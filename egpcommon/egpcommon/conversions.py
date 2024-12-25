"""Data type conversions for GC fields.

The need for type conversions is driven by:
    a) Efficient database storage types
    b) Efficient python code execution types
    c) Limitations of human readable file formats i.e. JSON
"""

from json import dumps, loads
from zlib import compress, decompress

from numpy import frombuffer, ndarray, uint8
from numpy.typing import NDArray

from egpcommon.common import NULL_SHA256, PROPERTIES
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def compress_json(
    obj: dict | list | memoryview | bytearray | bytes | None,
) -> bytes | memoryview | bytearray | None:
    """Compress a JSON dict object.

    Args
    ----
    obj (dict): Must be a JSON compatible dict.

    Returns
    -------
    (bytes): zlib compressed JSON string.
    """
    if isinstance(obj, dict):
        return compress(dumps(obj).encode())
    if isinstance(obj, (memoryview, bytearray, bytes)):
        return obj
    if obj is None:
        return None
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'dict' or byte type.")


def decompress_json(obj: bytes | None) -> dict | list | None:
    """Decompress a compressed JSON dict object.

    Args
    ----
    obj (bytes): zlib compressed JSON string.

    Returns
    -------
    (dict): JSON dict.
    """
    return None if obj is None else loads(decompress(obj).decode())


def memoryview_to_bytes(obj: memoryview | None) -> bytes | None:
    """Convert a memory view to a bytes object.

    Args
    ----
    obj (memoryview or NoneType):

    Returns
    -------
    (bytes or NoneType)
    """
    return None if obj is None else bytes(obj)


def memoryview_to_ndarray(obj: memoryview | None) -> NDArray | None:
    """Convert a memory view to a 32 uint8 numpy ndarray.

    Args
    ----
    obj (memoryview or NoneType):

    Returns
    -------
    (numpy.ndarray or NoneType)
    """
    return None if obj is None else frombuffer(obj, dtype=uint8, count=32)


def ndarray_to_memoryview(obj: NDArray | bytes | None) -> memoryview | None:
    """Convert a numpy 32 uint8 ndarray to a memory view.

    Args
    ----
    obj (numpy.ndarray or NoneType):

    Returns
    -------
    (memoryview or NoneType)
    """
    if isinstance(obj, ndarray):
        return obj.data
    if isinstance(obj, memoryview) or obj is None:
        return obj
    if isinstance(obj, (bytes, bytearray)):
        return memoryview(obj)
    assert False, f"Un-encodeable type '{type(obj)}': Expected 'ndarray' or byte type."


def ndarray_to_bytes(obj: NDArray | bytes | None) -> bytes | None:
    """Convert a numpy 32 uint8 ndarray to a bytes object.

    Args
    ----
    obj (numpy.ndarray or NoneType):

    Returns
    -------
    (bytes or NoneType)
    """
    if isinstance(obj, ndarray):
        return obj.tobytes()
    if isinstance(obj, bytes) or obj is None:
        return obj
    assert False, "Un-encodeable type"


def encode_properties(obj: dict[str, bool] | int | None) -> int:
    """Encode the properties dictionary into its integer representation.

    The properties field is a dictionary of properties to boolean values. Each
    property maps to a specific bit of a 64 bit value as defined
    by the _PROPERTIES dictionary.

    Args
    ----
    obj(dict): Properties dictionary.

    Returns
    -------
    (int): Integer representation of the properties dictionary.
    """
    if isinstance(obj, dict):
        bitfield: int = 0
        for k in (x[0] for x in obj.items() if x[1]):
            bitfield |= PROPERTIES[k]
        return bitfield
    if isinstance(obj, int):
        return obj
    if obj is None:
        return 0
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'dict' or integer type.")


def decode_properties(obj: int | dict[str, bool] | None) -> dict[str, bool]:
    """Decode the properties dictionary from its integer representation.

    The properties field is a dictionary of properties to boolean values. Each
    property maps to a specific bit of a 64 bit value as defined
    by the _PROPERTIES dictionary.

    Args
    ----
    obj(int): Integer representation of the properties dictionary.

    Returns
    -------
    (dict): Properties dictionary.
    """
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, int):
        return {b: bool(f & obj) for b, f in PROPERTIES.items()}
    if obj is None:
        return {b: False for b, f in PROPERTIES.items()}
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'dict' or integer type.")


def list_int_to_bytes(obj: list[int] | None) -> bytes | None:
    """Convert a list of integers to a bytes object.

    Args
    ----
    obj (list[int] or NoneType):

    Returns
    -------
    (bytes or NoneType)
    """
    return None if obj is None else bytes(obj)


def bytes_to_list_int(obj: bytes | None) -> list[int] | None:
    """Convert a bytes object to a list of integers.

    Args
    ----
    obj (bytes or NoneType):

    Returns
    -------
    (list[int] or NoneType)
    """
    return None if obj is None else list(obj)


def null_sha256_to_none(obj: bytes | None) -> bytes | None:
    """Convert a null signature to None.

    Args
    ----
    obj (bytes or NoneType):

    Returns
    -------
    (bytes or NoneType)
    """
    return None if obj is NULL_SHA256 or obj == NULL_SHA256 else obj
