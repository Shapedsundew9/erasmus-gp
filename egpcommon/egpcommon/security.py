"""Security functions for EGPPY."""

import base64
import hashlib
import json
import os
from datetime import UTC, datetime
from json import dump, load
from os.path import getsize
from typing import Any
from uuid import UUID

from cryptography.exceptions import InvalidSignature as CryptographyInvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Custom Exceptions
class InvalidSignatureError(Exception):
    """Raised when a signature verification fails."""


class HashMismatchError(Exception):
    """Raised when a file hash does not match the expected hash."""


# JSON filesize limit
JSON_FILESIZE_LIMIT = 2**30  # 1 GB


def _compute_file_hash(filepath: str) -> str:
    """Compute the SHA-256 hash of a file.

    Args:
        filepath: Path to the file to hash.

    Returns:
        Hexadecimal string representation of the SHA-256 hash.
    """
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def sign_file(
    filepath: str,
    private_key_pem: str,
    creator_uuid: UUID,
    algorithm: str = "Ed25519",
) -> str:
    """Sign a file using its SHA-256 hash and create a detached signature file.

    Args:
        filepath: Path to the file to sign.
        private_key_pem: Private key in PEM format.
        creator_uuid: UUID of the creator signing the file.
        algorithm: Signature algorithm to use ("Ed25519" or "RSA"). Defaults to "Ed25519".

    Returns:
        Path to the created .sig file.

    Raises:
        FileNotFoundError: If the file to sign does not exist.
        ValueError: If the algorithm is not supported or key format is invalid.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Compute the SHA-256 hash of the file
    file_hash = _compute_file_hash(filepath)

    # Load the private key
    private_key_bytes = private_key_pem.encode("utf-8")

    if algorithm == "Ed25519":
        try:
            private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
            if not isinstance(private_key, ed25519.Ed25519PrivateKey):
                raise ValueError("Private key is not an Ed25519 key")
        except Exception as e:
            raise ValueError(f"Failed to load Ed25519 private key: {e}") from e

        # Sign the hash
        signature_bytes = private_key.sign(file_hash.encode("utf-8"))

    elif algorithm == "RSA":
        try:
            private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
            if not isinstance(private_key, rsa.RSAPrivateKey):
                raise ValueError("Private key is not an RSA key")
        except Exception as e:
            raise ValueError(f"Failed to load RSA private key: {e}") from e

        # Sign the hash using RSA with PSS padding
        signature_bytes = private_key.sign(
            file_hash.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    # Encode signature in base64
    signature_b64 = base64.b64encode(signature_bytes).decode("utf-8")

    # Create signature metadata
    sig_data: dict[str, Any] = {
        "creator_uuid": str(creator_uuid),
        "file_hash": file_hash,
        "signature": signature_b64,
        "algorithm": algorithm,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Write signature to .sig file
    sig_filepath = f"{filepath}.sig"
    with open(sig_filepath, "w", encoding="utf-8") as f:
        dump(sig_data, f, indent=2)

    return sig_filepath


def verify_file_signature(  # pylint: disable=too-many-branches
    filepath: str,
    public_key_pem: str,
    sig_filepath: str | None = None,
) -> bool:
    """Verify a file's signature using a detached signature file.

    Args:
        filepath: Path to the file to verify.
        public_key_pem: Public key in PEM format.
        sig_filepath: Path to the .sig file. If None, assumes <filepath>.sig

    Returns:
        True if the signature is valid.

    Raises:
        FileNotFoundError: If the file or signature file does not exist.
        InvalidSignatureError: If the signature verification fails.
        HashMismatchError: If the file hash doesn't match the hash in the signature file.
        ValueError: If the algorithm is not supported or signature data is invalid.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if sig_filepath is None:
        sig_filepath = f"{filepath}.sig"

    if not os.path.exists(sig_filepath):
        raise FileNotFoundError(f"Signature file not found: {sig_filepath}")

    # Load signature metadata
    with open(sig_filepath, "r", encoding="utf-8") as f:
        sig_data = load(f)

    # Validate required fields
    required_fields = ["file_hash", "signature", "algorithm", "creator_uuid"]
    for field in required_fields:
        if field not in sig_data:
            raise ValueError(f"Missing required field in signature file: {field}")

    stored_hash = sig_data["file_hash"]
    signature_b64 = sig_data["signature"]
    algorithm = sig_data["algorithm"]

    # Compute current file hash
    current_hash = _compute_file_hash(filepath)

    # Verify hash matches
    if current_hash != stored_hash:
        raise HashMismatchError(f"File hash mismatch. Expected: {stored_hash}, Got: {current_hash}")

    # Decode signature
    try:
        signature_bytes = base64.b64decode(signature_b64)
    except Exception as e:
        raise ValueError(f"Failed to decode signature: {e}") from e

    # Load public key and verify signature
    public_key_bytes = public_key_pem.encode("utf-8")

    if algorithm == "Ed25519":
        try:
            public_key = serialization.load_pem_public_key(public_key_bytes)
            if not isinstance(public_key, ed25519.Ed25519PublicKey):
                raise ValueError("Public key is not an Ed25519 key")
        except Exception as e:
            raise ValueError(f"Failed to load Ed25519 public key: {e}") from e

        try:
            public_key.verify(signature_bytes, stored_hash.encode("utf-8"))
        except CryptographyInvalidSignature as e:
            raise InvalidSignatureError("Signature verification failed") from e

    elif algorithm == "RSA":
        try:
            public_key = serialization.load_pem_public_key(public_key_bytes)
            if not isinstance(public_key, rsa.RSAPublicKey):
                raise ValueError("Public key is not an RSA key")
        except Exception as e:
            raise ValueError(f"Failed to load RSA public key: {e}") from e

        try:
            public_key.verify(
                signature_bytes,
                stored_hash.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        except CryptographyInvalidSignature as e:
            raise InvalidSignatureError(f"Signature verification failed (algorithm: {algorithm})") from e
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return True


def dump_signed_json(data: dict | list, fullpath: str) -> None:
    """Dump a signed JSON file.

    The most compact JSON format is used to reduce file size. The assumption is that
    the file, if viewed will be done with a JSON capable viewer.
    Sign with this creator's UUID & signature and dump the JSON object.
    """
    # TODO: Implementation Needed
    with open(fullpath, "w", encoding="utf-8") as f:
        dump(data, f, indent=2, sort_keys=True, ensure_ascii=True)
    # Prevents continuing with a file we can't read
    _file_size_limit(fullpath, JSON_FILESIZE_LIMIT)


def _file_size_limit(fullpath: str, limit: int = 2**30) -> int:
    """Check if the file size is within the limit."""
    size = getsize(fullpath)
    if size > limit:
        raise ValueError(f"File {fullpath} size {size} exceeds limit {limit}.")
    return size


def validate_json_signature(fullpath: str) -> bool:  # pylint: disable=unused-argument
    """Validate the JSON file signature.
    EGP JSON files are always a list. The first element of the list is the
    data and the second element is the signature.
    No matter how the data is formatted the signed JSON always has this format:
    [
    <data object>,
    "lowercase hexadecimal signature[64]",
    ]
    The signature is thus always characters 1 to 64 inclusive of the penultimate line.
    The signature is the signed sha256 hash of characters from the start of the file to
    the end of the antepenultimate line inclusive (i.e. including the comma after
    the data object).
    Validation ensures that the format of the signature line and the last line are exact.
    """
    # TODO: Implementation Needed
    return True


def get_signature(creator: UUID) -> bytes:  # pylint: disable=unused-argument
    """Get the creators signature.
    May be the local creator, Erasmus, or a validated community creator.
    """
    return bytes()  # TODO: Implementation Needed


def load_signed_json(fullpath: str) -> dict | list:
    """Load a signed JSON file.

    Validate that creator UUID and signature is correct and return the JSON object.
    """
    _file_size_limit(fullpath, JSON_FILESIZE_LIMIT)
    with open(fullpath, "r", encoding="ascii") as fileptr:
        return load(fileptr)


def load_signed_json_dict(fullpath: str) -> dict:
    """Load a signed JSON file as a dictionary."""
    data = load_signed_json(fullpath)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a dictionary, got {type(data)}")
    return data


def load_signed_json_list(fullpath: str) -> list:
    """Load a signed JSON file as a list."""
    data = load_signed_json(fullpath)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list, got {type(data)}")
    return data
