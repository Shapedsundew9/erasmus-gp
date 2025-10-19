"""Unit tests for the security module."""

import json
import os
import tempfile
from unittest import TestCase
from uuid import uuid4

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from egpcommon.security import (
    HashMismatchError,
    InvalidSignatureError,
    _compute_file_hash,
    sign_file,
    verify_file_signature,
)


class TestSecurity(TestCase):  # pylint: disable=too-many-instance-attributes
    """Test cases for the security module."""

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

    def _create_test_file(self, content: str, filename: str = "test_file.txt") -> str:
        """Helper method to create a test file."""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

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

    def test_sign_file_not_found(self) -> None:
        """Test signing a non-existent file raises FileNotFoundError."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")

        with self.assertRaises(FileNotFoundError):
            sign_file(nonexistent_file, self.ed25519_private_pem, self.creator_uuid)

    def test_sign_file_invalid_algorithm(self) -> None:
        """Test signing with an unsupported algorithm raises ValueError."""
        filepath = self._create_test_file("Test content")

        with self.assertRaises(ValueError) as context:
            sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="INVALID")

        self.assertIn("Unsupported algorithm", str(context.exception))

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

    def test_verify_file_signature_rsa_success(self) -> None:
        """Test successful signature verification with RSA."""
        # Create and sign test file
        filepath = self._create_test_file("Test content for RSA verification")
        sig_filepath = sign_file(filepath, self.rsa_private_pem, self.creator_uuid, algorithm="RSA")

        # Verify signature
        result = verify_file_signature(filepath, self.rsa_public_pem, sig_filepath)
        self.assertTrue(result)

    def test_verify_file_signature_default_sig_path(self) -> None:
        """Test signature verification with default .sig file path."""
        # Create and sign test file
        filepath = self._create_test_file("Test content")
        sign_file(filepath, self.ed25519_private_pem, self.creator_uuid, algorithm="Ed25519")

        # Verify signature without specifying sig_filepath
        result = verify_file_signature(filepath, self.ed25519_public_pem)
        self.assertTrue(result)

    def test_verify_file_signature_file_not_found(self) -> None:
        """Test verification fails when file doesn't exist."""
        nonexistent_file = os.path.join(self.test_dir, "nonexistent.txt")

        with self.assertRaises(FileNotFoundError):
            verify_file_signature(nonexistent_file, self.ed25519_public_pem)

    def test_verify_file_signature_sig_file_not_found(self) -> None:
        """Test verification fails when signature file doesn't exist."""
        filepath = self._create_test_file("Test content")

        with self.assertRaises(FileNotFoundError):
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
        original_uuid = sig_data["creator_uuid"]
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
