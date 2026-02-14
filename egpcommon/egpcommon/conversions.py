"""Data type conversions for GC fields.

The need for type conversions is driven by:
    a) Efficient database storage types
    b) Efficient python code execution types
    c) Limitations of human readable file formats i.e. JSON

Conversions behave as follows:
    a) Output types shall be limited to the type required by the application or DB.
    b) Input types may be any type reasonably convertible to the output type.
"""

from json import dumps, loads
from zlib import compress, decompress

from numpy import frombuffer, ndarray, uint8
from numpy.typing import NDArray

from egpcommon.deduplication import signature_store
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.properties import PropertiesBD

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


def bytes_to_list_int(obj: bytes | None) -> list[int] | None:
    """Convert a bytes object to a list of integers.

    Args:
        obj: bytes to convert, or None.

    Returns:
        List of integers, or None if input is None.
    """
    return None if obj is None else list(obj)


def compress_json(
    obj: dict | list | memoryview | bytearray | bytes | None,
) -> bytes | memoryview | bytearray | None:
    """Compress a JSON dict object.

    Args:
        obj: Must be a JSON compatible dict, byte-like, or None.

    Returns:
        zlib compressed JSON string as bytes, or the original byte-like.

    Raises:
        TypeError: If obj is not a dict, byte type, or None.
    """
    if isinstance(obj, dict):
        return compress(dumps(obj).encode())
    if isinstance(obj, (memoryview, bytearray, bytes)):
        return obj
    if obj is None:
        return None
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'dict' or byte type.")


def decode_properties(properties: dict | int) -> dict:
    """Decode properties."""
    return PropertiesBD(properties).to_json() if isinstance(properties, int) else properties


def decompress_json(obj: bytes | None) -> dict | list | None:
    """Decompress a compressed JSON dict object.

    Args:
        obj: zlib compressed JSON string, or None.

    Returns:
        Decompressed JSON dict/list, or None if input is None.
    """
    return None if obj is None else loads(decompress(obj).decode())


def encode_properties(properties: dict | int) -> int:
    """Encode properties."""
    return PropertiesBD(properties).to_int() if isinstance(properties, dict) else properties


def list_int_to_bytes(obj: list[int] | bytes | None) -> bytes | None:
    """Convert a list of integers to a bytes object.

    Args:
        obj: List of integers, bytes, or None.

    Returns:
        Bytes object, or None if input is None.
    """
    # A bytes(bytes) call returns the same object as bytes are immutable.
    return None if obj is None else bytes(obj)


def memoryview_to_bytes(obj: memoryview | None) -> bytes | None:
    """Convert a memory view to a bytes object.

    Args:
        obj: Memoryview to convert, or None.

    Returns:
        Bytes object, or None if input is None.
    """
    return None if obj is None else bytes(obj)


def memoryview_to_ndarray(obj: memoryview | None) -> NDArray | None:
    """Convert a memory view to a 32 uint8 numpy ndarray.

    Args:
        obj: Memoryview to convert, or None.

    Returns:
        Numpy ndarray of 32 uint8 values, or None if input is None.
    """
    return None if obj is None else frombuffer(obj, dtype=uint8, count=32)


def memoryview_to_signature(obj: memoryview | None) -> bytes | None:
    """Convert a memory view to a signature bytes object.

    Signatures are de-duplicated.

    Args:
        obj: Memoryview to convert, or None.

    Returns:
        De-duplicated signature bytes, or None if input is None.
    """
    return None if obj is None else signature_store[bytes(obj)]


def ndarray_to_bytes(obj: NDArray | bytes | None) -> bytes | None:
    """Convert a numpy uint8 ndarray to a bytes object.

    Args:
        obj: Numpy ndarray, bytes, or None.

    Returns:
        Bytes object, or None if input is None.

    Raises:
        TypeError: If obj is not an ndarray, bytes, or None.
    """
    if isinstance(obj, ndarray):
        return obj.tobytes()
    if isinstance(obj, bytes) or obj is None:
        return obj
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'ndarray', 'bytes', or None.")


def ndarray_to_memoryview(obj: NDArray | bytes | None) -> memoryview | None:
    """Convert a numpy uint8 ndarray to a memory view.

    Args:
        obj: Numpy ndarray, bytes/bytearray, memoryview, or None.

    Returns:
        Memoryview, or None if input is None.

    Raises:
        TypeError: If obj is not an ndarray, byte type, memoryview, or None.
    """
    if isinstance(obj, ndarray):
        return obj.data
    if isinstance(obj, memoryview) or obj is None:
        return obj
    if isinstance(obj, (bytes, bytearray)):
        return memoryview(obj)
    raise TypeError(f"Un-encodeable type '{type(obj)}': Expected 'ndarray' or byte type.")
