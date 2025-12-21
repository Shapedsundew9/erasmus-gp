"""Unit tests for the security module."""

import json
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from egpcommon.common import SHAPEDSUNDEW9_UUID
from egpcommon.security import (
    JSON_FILESIZE_LIMIT,
    HashMismatchError,
    InvalidSignatureError,
    _compute_file_hash,
    dump_signed_json,
    load_signed_json,
    load_signed_json_dict,
    load_signed_json_list,
    sign_file,
    verify_file_signature,
)


class TestSecurity(TestCase):  # pylint: disable=too-many-instance-attributes
    """Test cases for the security module."""

    def _create_test_file(self, content: str, filename: str = "test_file.txt") -> str:
        """Helper method to create a test file."""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Generate Ed25519 key pair
        self.ed25519_private_key = ed25519.Ed25519PrivateKey.generate()
        self.ed25519_public_key = self.ed25519_private_key.public_key()

        # Serialize keys to PEM format
        self.ed25519_private_pem = self.ed25519_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        self.ed25519_public_pem = self.ed25519_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        # Generate RSA key pair (2048 bits for faster tests)
        self.rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.rsa_public_key = self.rsa_private_key.public_key()

        # Serialize RSA keys to PEM format
        self.rsa_private_pem = self.rsa_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        self.rsa_public_pem = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        # Create test UUID
        self.creator_uuid = uuid4()

    def tearDown(self) -> None:
        """Clean up test files."""
        # Remove all files in test directory
        for filename in os.listdir(self.test_dir):
            filepath = os.path.join(self.test_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        os.rmdir(self.test_dir)

    def test_compute_file_hash(self) -> None:
        """Test the _compute_file_hash function."""
        # Create a test file with known content
        content = "Test content for hashing"
        filepath = self._create_test_file(content)

        # Compute hash
        file_hash = _compute_file_hash(filepath)

        # Verify hash is a 64-character hex string (SHA-256)
        self.assertEqual(len(file_hash), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in file_hash))

        # Verify hash is consistent
        file_hash2 = _compute_file_hash(filepath)
        self.assertEqual(file_hash, file_hash2)

    def test_invalid_base64_signature(self) -> None:
        """Test that invalid base64 in signature is properly rejected."""
        # Create and sign test file
        filepath = self._create_test_file("Test content")
        sig_filepath = sign_file(
            filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519"
        )

        # Load and corrupt signature with invalid base64
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)

        # Add invalid characters to base64
        sig_data["signature"] = "not!valid@base64#"

        with open(sig_filepath, "w", encoding="utf-8") as f:
            json.dump(sig_data, f)

        # Verify should fail with ValueError mentioning base64
        with self.assertRaises(ValueError) as context:
            verify_file_signature(filepath, self.ed25519_public_pem, sig_filepath)

        self.assertIn("base64", str(context.exception).lower())

    def test_metadata_tampering_detection(self) -> None:
        """Test that tampering with metadata (creator_uuid or algorithm) is detected."""
        # Create and sign test file
        filepath = self._create_test_file("Test content for metadata tampering")
        sig_filepath = sign_file(
            filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519"
        )

        # Load signature file
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)

        # Tamper with creator_uuid
        sig_data["creator_uuid"] = str(uuid4())
        with open(sig_filepath, "w", encoding="utf-8") as f:
            json.dump(sig_data, f)

        # Verify should fail due to signature not covering tampered metadata
        with self.assertRaises(InvalidSignatureError):
            verify_file_signature(filepath, self.ed25519_public_pem, sig_filepath)

        # Restore and tamper with file_hash (but keep file unchanged)
        sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519")
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)

        # Tamper with the hash directly
        sig_data["file_hash"] = "0" * 64  # Invalid hash
        with open(sig_filepath, "w", encoding="utf-8") as f:
            json.dump(sig_data, f)

        # Should fail with hash mismatch first
        with self.assertRaises(HashMismatchError):
            verify_file_signature(filepath, self.ed25519_public_pem, sig_filepath)

    def test_multiple_signatures(self) -> None:
        """Test that signing the same file multiple times produces valid signatures."""
        filepath = self._create_test_file("Test content")

        # Sign twice
        sig_filepath1 = sign_file(
            filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519"
        )

        with open(sig_filepath1, "r", encoding="utf-8") as f:
            sig_data1 = json.load(f)

        # Sign again (overwriting the first signature)
        sig_filepath2 = sign_file(
            filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519"
        )

        with open(sig_filepath2, "r", encoding="utf-8") as f:
            sig_data2 = json.load(f)

        # The file hash and creator should be the same
        self.assertEqual(sig_data1["file_hash"], sig_data2["file_hash"])
        self.assertEqual(sig_data1["creator_uuid"], sig_data2["creator_uuid"])

        # Verify timestamp field exists
        self.assertIsNotNone(sig_data2["timestamp"])
        self.assertIsNotNone(sig_data2["algorithm"])

        # Verify signature is valid
        result = verify_file_signature(filepath, self.ed25519_public_pem)
        self.assertTrue(result)

    def test_sign_and_verify_large_file(self) -> None:
        """Test signing and verifying a larger file."""
        # Create a larger test file (1 MB)
        large_content = "A" * (1024 * 1024)
        filepath = self._create_test_file(large_content, "large_file.txt")

        # Sign the file
        sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519")

        # Verify signature
        result = verify_file_signature(filepath, self.ed25519_public_pem)
        self.assertTrue(result)

    def test_sign_binary_file(self) -> None:
        """Test signing a binary file."""
        # Create a binary test file
        filepath = os.path.join(self.test_dir, "binary_file.bin")
        binary_content = bytes(range(256))
        with open(filepath, "wb") as f:
            f.write(binary_content)

        # Sign the file
        sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519")

        # Verify signature
        result = verify_file_signature(filepath, self.ed25519_public_pem)
        self.assertTrue(result)

    def test_sign_file_ed25519(self) -> None:
        """Test signing a file with Ed25519."""
        # Create test file
        filepath = self._create_test_file("Test content for signing")

        # Sign the file
        sig_filepath = sign_file(
            filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519"
        )

        # Verify signature file was created
        self.assertTrue(os.path.exists(sig_filepath))
        self.assertEqual(sig_filepath, f"{filepath}.sig")

        # Load and verify signature file structure
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)

        self.assertIn("creator_uuid", sig_data)
        self.assertIn("file_hash", sig_data)
        self.assertIn("signature", sig_data)
        self.assertIn("algorithm", sig_data)
        self.assertIn("timestamp", sig_data)

        self.assertEqual(sig_data["creator_uuid"], str(self.creator_uuid))
        self.assertEqual(sig_data["algorithm"], "Ed25519")

    def test_sign_file_invalid_algorithm(self) -> None:
        """Test signing with an unsupported algorithm raises ValueError."""
        filepath = self._create_test_file("Test content")

        with self.assertRaises(ValueError) as context:
            sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="INVALID")

        self.assertIn("Unsupported algorithm", str(context.exception))

    def test_sign_file_not_found(self) -> None:
        """Test signing a non-existent file raises FileNotFoundError."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")

        with self.assertRaises(FileNotFoundError):
            sign_file(nonexistent_file, self.ed25519_private_pem, self.creator_uuid)

    def test_sign_file_rsa(self) -> None:
        """Test signing a file with RSA."""
        # Create test file
        filepath = self._create_test_file("Test content for RSA signing")

        # Sign the file
        sig_filepath = sign_file(filepath, self.rsa_private_pem, self.creator_uuid, algorithm="RSA")

        # Verify signature file was created
        self.assertTrue(os.path.exists(sig_filepath))

        # Load and verify signature file structure
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)

        self.assertEqual(sig_data["algorithm"], "RSA")

    def test_verify_file_signature_default_sig_path(self) -> None:
        """Test signature verification with default .sig file path."""
        # Create and sign test file
        filepath = self._create_test_file("Test content")
        sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519")

        # Verify signature without specifying sig_filepath
        result = verify_file_signature(filepath, self.ed25519_public_pem)
        self.assertTrue(result)

    def test_verify_file_signature_ed25519_success(self) -> None:
        """Test successful signature verification with Ed25519."""
        # Create and sign test file
        filepath = self._create_test_file("Test content for verification")
        sig_filepath = sign_file(
            filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519"
        )

        # Verify signature
        result = verify_file_signature(filepath, self.ed25519_public_pem, sig_filepath)
        self.assertTrue(result)

    def test_verify_file_signature_file_not_found(self) -> None:
        """Test verification fails when file doesn't exist."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")

        with self.assertRaises(FileNotFoundError):
            verify_file_signature(nonexistent_file, self.ed25519_public_pem)

    def test_verify_file_signature_hash_mismatch(self) -> None:
        """Test verification fails when file content changes."""
        # Create and sign test file
        filepath = self._create_test_file("Original content")
        sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519")

        # Modify file content
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("Modified content")

        # Verify should fail due to hash mismatch
        with self.assertRaises(HashMismatchError):
            verify_file_signature(filepath, self.ed25519_public_pem)

    def test_verify_file_signature_invalid_signature(self) -> None:
        """Test verification fails with wrong public key."""
        # Create and sign test file
        filepath = self._create_test_file("Test content")
        sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519")

        # Generate a different key pair
        different_private_key = ed25519.Ed25519PrivateKey.generate()
        different_public_pem = (
            different_private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )

        # Verify with wrong public key should fail
        with self.assertRaises(InvalidSignatureError):
            verify_file_signature(filepath, different_public_pem)

    def test_verify_file_signature_missing_required_field(self) -> None:
        """Test verification fails when signature file is missing required fields."""
        # Create and sign test file
        filepath = self._create_test_file("Test content")
        sig_filepath = sign_file(
            filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519"
        )

        # Load and corrupt signature file
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)

        # Remove a required field
        del sig_data["file_hash"]

        with open(sig_filepath, "w", encoding="utf-8") as f:
            json.dump(sig_data, f)

        # Verify should fail
        with self.assertRaises(ValueError) as context:
            verify_file_signature(filepath, self.ed25519_public_pem, sig_filepath)

        self.assertIn("Missing required field", str(context.exception))

    def test_verify_file_signature_rsa_success(self) -> None:
        """Test successful signature verification with RSA."""
        # Create and sign test file
        filepath = self._create_test_file("Test content for RSA verification")
        sig_filepath = sign_file(filepath, self.rsa_private_pem, self.creator_uuid, algorithm="RSA")

        # Verify signature
        result = verify_file_signature(filepath, self.rsa_public_pem, sig_filepath)
        self.assertTrue(result)

    def test_verify_file_signature_sig_file_not_found(self) -> None:
        """Test verification fails when signature file doesn't exist."""
        filepath = self._create_test_file("Test content")

        with self.assertRaises(FileNotFoundError):
            verify_file_signature(filepath, self.ed25519_public_pem)


class TestSignedJSON(TestCase):  # pylint: disable=too-many-instance-attributes
    """Test cases for signed JSON functions."""

    def _mock_load_private_key(self, _: str) -> ed25519.Ed25519PrivateKey:
        """Mock function for load_private_key."""
        return self.ed25519_private_key

    def _mock_load_public_key(self, _: str) -> ed25519.Ed25519PublicKey:
        """Mock function for load_public_key."""
        return self.ed25519_public_key

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Generate Ed25519 key pair for testing
        self.ed25519_private_key = ed25519.Ed25519PrivateKey.generate()
        self.ed25519_public_key = self.ed25519_private_key.public_key()

        # Serialize keys to PEM format
        self.ed25519_private_pem = self.ed25519_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        self.ed25519_public_pem = self.ed25519_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Generate RSA key pair for testing
        self.rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.rsa_public_key = self.rsa_private_key.public_key()

        # Serialize RSA keys to PEM format
        self.rsa_private_pem = self.rsa_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        self.rsa_public_pem = self.rsa_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def tearDown(self) -> None:
        """Clean up test files."""
        # Remove all files in test directory
        for filename in os.listdir(self.test_dir):
            filepath = os.path.join(self.test_dir, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)
        os.rmdir(self.test_dir)

    def test_dump_signed_json_canonical_format(self) -> None:
        """Test that dump_signed_json creates canonical JSON with sorted keys."""
        test_data = {"z_key": 1, "a_key": 2, "m_key": 3}
        filepath = os.path.join(self.test_dir, "test_canonical.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Read the raw file content
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Verify keys are sorted (a_key should come before m_key, which comes before z_key)
        a_pos = content.find('"a_key"')
        m_pos = content.find('"m_key"')
        z_pos = content.find('"z_key"')
        self.assertLess(a_pos, m_pos)
        self.assertLess(m_pos, z_pos)

    def test_dump_signed_json_complex_nested_structure(self) -> None:
        """Test dumping and loading complex nested JSON structures."""
        test_data = {
            "level1": {
                "level2": {
                    "level3": ["item1", "item2", {"level4": "value"}],
                    "numbers": [1, 2, 3.14, -42],
                },
                "boolean": True,
                "null_value": None,
            },
            "list_of_dicts": [{"a": 1}, {"b": 2}, {"c": 3}],
        }
        filepath = os.path.join(self.test_dir, "test_complex.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Load and verify
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            loaded_data = load_signed_json_dict(filepath)

        self.assertEqual(loaded_data, test_data)

    def test_dump_signed_json_dict(self) -> None:
        """Test dumping a signed JSON dictionary."""
        test_data = {"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        filepath = os.path.join(self.test_dir, "test_dict.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Verify the JSON file was created
        self.assertTrue(os.path.exists(filepath))

        # Verify the signature file was created
        sig_filepath = f"{filepath}.sig"
        self.assertTrue(os.path.exists(sig_filepath))

        # Verify the JSON content is correct
        with open(filepath, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)

        # Verify signature metadata
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)
        self.assertIn("creator_uuid", sig_data)
        self.assertIn("file_hash", sig_data)
        self.assertIn("signature", sig_data)
        self.assertIn("algorithm", sig_data)
        self.assertEqual(sig_data["creator_uuid"], str(SHAPEDSUNDEW9_UUID))

    def test_dump_signed_json_empty_dict(self) -> None:
        """Test dumping and loading an empty dictionary."""
        test_data: dict = {}
        filepath = os.path.join(self.test_dir, "test_empty_dict.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Load and verify
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            loaded_data = load_signed_json_dict(filepath)

        self.assertEqual(loaded_data, test_data)

    def test_dump_signed_json_empty_list(self) -> None:
        """Test dumping and loading an empty list."""
        test_data: list = []
        filepath = os.path.join(self.test_dir, "test_empty_list.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Load and verify
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            loaded_data = load_signed_json_list(filepath)

        self.assertEqual(loaded_data, test_data)

    def test_dump_signed_json_file_size_limit(self) -> None:
        """Test that dumping very large JSON raises ValueError."""
        # Mock the limit to a small value to speed up the test
        small_limit = 1000

        # Create data that will exceed the mocked limit when serialized
        # Using a large string to make the JSON file very large
        large_data = {"data": "x" * (small_limit + 100)}
        filepath = os.path.join(self.test_dir, "test_large.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                with patch("egpcommon.security.JSON_FILESIZE_LIMIT", small_limit):
                    with self.assertRaises(ValueError) as context:
                        dump_signed_json(large_data, filepath)

        self.assertIn("exceeds limit", str(context.exception))

    def test_dump_signed_json_list(self) -> None:
        """Test dumping a signed JSON list."""
        test_data = [1, 2, 3, "four", {"five": 5}]
        filepath = os.path.join(self.test_dir, "test_list.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Verify the JSON file was created
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(os.path.exists(f"{filepath}.sig"))

        # Verify the JSON content is correct
        with open(filepath, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)

    def test_dump_signed_json_rsa_algorithm(self) -> None:
        """Test that dump_signed_json works with RSA keys."""

        def mock_load_rsa_private_key(_: str) -> rsa.RSAPrivateKey:
            return self.rsa_private_key

        def mock_load_rsa_public_key(_: str) -> rsa.RSAPublicKey:
            return self.rsa_public_key

        test_data = {"algorithm": "RSA"}
        filepath = os.path.join(self.test_dir, "test_rsa.json")

        with patch("egpcommon.security.load_private_key", mock_load_rsa_private_key):
            with patch("egpcommon.security.load_public_key", mock_load_rsa_public_key):
                dump_signed_json(test_data, filepath)

        # Verify signature file has RSA algorithm
        sig_filepath = f"{filepath}.sig"
        with open(sig_filepath, "r", encoding="utf-8") as f:
            sig_data = json.load(f)
        self.assertEqual(sig_data["algorithm"], "RSA")

        # Load and verify
        with patch("egpcommon.security.load_public_key", mock_load_rsa_public_key):
            loaded_data = load_signed_json_dict(filepath)

        self.assertEqual(loaded_data, test_data)

    def test_dump_signed_json_unicode_characters(self) -> None:
        """Test dumping and loading JSON with unicode characters."""
        test_data = {
            "english": "Hello",
            "spanish": "¡Hola!",
            "chinese": "你好",
            "emoji": "🚀🐍",
            "special": "\\n\\t\\r",
        }
        filepath = os.path.join(self.test_dir, "test_unicode.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Load and verify
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            loaded_data = load_signed_json_dict(filepath)

        self.assertEqual(loaded_data, test_data)

    def test_load_signed_json_dict(self) -> None:
        """Test loading a signed JSON dictionary."""
        test_data = {"key1": "value1", "key2": 42}
        filepath = os.path.join(self.test_dir, "test_load_dict.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Load the signed JSON
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            loaded_data = load_signed_json_dict(filepath)

        self.assertEqual(loaded_data, test_data)
        self.assertIsInstance(loaded_data, dict)

    def test_load_signed_json_dict_wrong_type(self) -> None:
        """Test that load_signed_json_dict raises ValueError for non-dict data."""
        test_data = [1, 2, 3]  # List, not dict
        filepath = os.path.join(self.test_dir, "test_wrong_type.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Try to load as dict should fail
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            with self.assertRaises(ValueError) as context:
                load_signed_json_dict(filepath)

        self.assertIn("Expected a dictionary", str(context.exception))

    def test_load_signed_json_file_size_limit(self) -> None:
        """Test that loading a file exceeding size limit raises ValueError."""
        # Create a valid signed JSON file first
        test_data = {"key": "value"}
        filepath = os.path.join(self.test_dir, "test_size_check.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Mock getsize to return a value exceeding the limit
        with patch("egpcommon.security.getsize", return_value=JSON_FILESIZE_LIMIT + 1):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                with self.assertRaises(ValueError) as context:
                    load_signed_json(filepath)

        self.assertIn("exceeds limit", str(context.exception))

    def test_load_signed_json_generic(self) -> None:
        """Test loading signed JSON with generic function."""
        test_data_dict = {"test": "data"}
        test_data_list = [1, 2, 3]

        filepath_dict = os.path.join(self.test_dir, "test_generic_dict.json")
        filepath_list = os.path.join(self.test_dir, "test_generic_list.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data_dict, filepath_dict)
                dump_signed_json(test_data_list, filepath_list)

        # Load both types
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            loaded_dict = load_signed_json(filepath_dict)
            loaded_list = load_signed_json(filepath_list)

        self.assertEqual(loaded_dict, test_data_dict)
        self.assertEqual(loaded_list, test_data_list)

    def test_load_signed_json_invalid_signature(self) -> None:
        """Test that loading fails with tampered signature."""
        test_data = {"key": "value"}
        filepath = os.path.join(self.test_dir, "test_tampered.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Tamper with the JSON content
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"key": "tampered_value"}, f)

        # Try to load should fail due to hash mismatch
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            with self.assertRaises(HashMismatchError):
                load_signed_json(filepath)

    def test_load_signed_json_list(self) -> None:
        """Test loading a signed JSON list."""
        test_data = [1, 2, 3, "test"]
        filepath = os.path.join(self.test_dir, "test_load_list.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Load the signed JSON
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            loaded_data = load_signed_json_list(filepath)

        self.assertEqual(loaded_data, test_data)
        self.assertIsInstance(loaded_data, list)

    def test_load_signed_json_list_wrong_type(self) -> None:
        """Test that load_signed_json_list raises ValueError for non-list data."""
        test_data = {"key": "value"}  # Dict, not list
        filepath = os.path.join(self.test_dir, "test_wrong_type_list.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Try to load as list should fail
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            with self.assertRaises(ValueError) as context:
                load_signed_json_list(filepath)

        self.assertIn("Expected a list", str(context.exception))

    def test_load_signed_json_missing_signature_file(self) -> None:
        """Test that loading fails when signature file is missing."""
        test_data = {"key": "value"}
        filepath = os.path.join(self.test_dir, "test_no_sig.json")

        with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                dump_signed_json(test_data, filepath)

        # Remove signature file
        sig_filepath = f"{filepath}.sig"
        os.remove(sig_filepath)

        # Try to load should fail
        with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
            with self.assertRaises(FileNotFoundError):
                load_signed_json(filepath)

    def test_multiple_dump_load_cycles(self) -> None:
        """Test multiple dump and load cycles preserve data integrity."""
        test_data = {"cycle": 0, "data": "test"}
        filepath = os.path.join(self.test_dir, "test_cycles.json")

        for i in range(3):
            test_data["cycle"] = i

            with patch("egpcommon.security.load_private_key", self._mock_load_private_key):
                with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                    dump_signed_json(test_data, filepath)

            with patch("egpcommon.security.load_public_key", self._mock_load_public_key):
                loaded_data = load_signed_json_dict(filepath)

            self.assertEqual(loaded_data, test_data)
            self.assertEqual(loaded_data["cycle"], i)
