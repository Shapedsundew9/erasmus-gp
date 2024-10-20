"""Test the conversions module."""

import unittest

from numpy import array, uint8
from numpy.testing import assert_array_equal

from egpcommon.common import PROPERTIES
from egpcommon.conversions import (
    bytes_to_list_int,
    compress_json,
    decode_properties,
    decompress_json,
    encode_properties,
    list_int_to_bytes,
    memoryview_to_bytes,
    memoryview_to_ndarray,
    ndarray_to_bytes,
    ndarray_to_memoryview,
)


class TestConversions(unittest.TestCase):
    """Test the conversions module."""

    def test_compress_json(self):
        """Test the compress_json function."""
        obj = {"key": "value"}
        compressed = compress_json(obj)
        self.assertIsInstance(compressed, bytes)

        with self.assertRaises(TypeError):
            compress_json("string")  # type: ignore

        self.assertIsNone(compress_json(None))

    def test_decompress_json(self):
        """Test the decompress_json function."""
        obj = {"key": "value"}
        compressed = compress_json(obj)
        decompressed = decompress_json(compressed)
        self.assertEqual(decompressed, obj)

        self.assertIsNone(decompress_json(None))

    def test_memoryview_to_bytes(self):
        """Test the memoryview_to_bytes function."""
        mv = memoryview(b"test")
        result = memoryview_to_bytes(mv)
        self.assertEqual(result, b"test")

        self.assertIsNone(memoryview_to_bytes(None))

    def test_memoryview_to_ndarray(self):
        """Test the memoryview_to_ndarray function."""
        mv = memoryview(b"test" * 8)
        result = memoryview_to_ndarray(mv)
        expected = array(list(b"test" * 8), dtype=uint8)
        assert_array_equal(result, expected)  # type: ignore

        self.assertIsNone(memoryview_to_ndarray(None))

    def test_ndarray_to_memoryview(self):
        """Test the ndarray_to_memoryview function."""
        arr = array(list(b"test" * 8), dtype=uint8)
        result = ndarray_to_memoryview(arr)
        assert isinstance(result, memoryview)
        self.assertEqual(result.tobytes(), b"test" * 8)

        self.assertIsNone(ndarray_to_memoryview(None))

    def test_ndarray_to_bytes(self):
        """Test the ndarray_to_bytes function."""
        arr = array(list(b"test" * 8), dtype=uint8)
        result = ndarray_to_bytes(arr)
        self.assertEqual(result, b"test" * 8)

    def test_encode_properties(self):
        """Test the encode_properties function."""
        properties_dict = {key: True for key in PROPERTIES}
        encoded = encode_properties(properties_dict)
        self.assertIsInstance(encoded, int)

        self.assertEqual(encode_properties(None), 0)

        with self.assertRaises(TypeError):
            encode_properties("string")  # type: ignore

    def test_decode_properties(self):
        """Test the decode_properties function."""
        properties_dict = {key: True for key in PROPERTIES}
        encoded = encode_properties(properties_dict)
        decoded = decode_properties(encoded)
        self.assertEqual(decoded, properties_dict)

        self.assertEqual(decode_properties(None), {key: False for key in PROPERTIES})

        with self.assertRaises(TypeError):
            decode_properties("string")  # type: ignore

    def test_list_int_to_bytes(self):
        """Test the list_int_to_bytes function."""
        data = [1, 2, 3]
        result = list_int_to_bytes(data)
        self.assertEqual(result, b"\x01\x02\x03")

        self.assertIsNone(list_int_to_bytes(None))

    def test_bytes_to_list_int(self):
        """Test the bytes_to_list_int function."""
        data = b"\x01\x02\x03"
        result = bytes_to_list_int(data)
        self.assertEqual(result, [1, 2, 3])

        self.assertIsNone(bytes_to_list_int(None))
