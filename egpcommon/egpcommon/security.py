"""Security functions for EGPPY."""

import base64
import binascii
import hashlib
import json
from datetime import UTC, datetime
from json import dump, load
from os import environ
from os.path import exists, getsize, join
from typing import Any
from uuid import UUID

from cryptography.exceptions import InvalidSignature as CryptographyInvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes

from egpcommon.common import SHAPEDSUNDEW9_UUID
from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Constants
PUBLIC_KEY_FOLDER = "/usr/local/share/egp/public_keys"
PRIVATE_KEY_FILE = environ.get("EGP_PRIVATE_KEY_FILE", "/run/secrets/private_key")


# Custom Exceptions
class InvalidSignatureError(Exception):
    """Raised when a signature verification fails."""


class HashMismatchError(Exception):
    """Raised when a file hash does not match the expected hash."""


# JSON filesize limit
JSON_FILESIZE_LIMIT = 2**30  # 1 GB


def load_private_key(private_key_path: str) -> PrivateKeyTypes:
    """Load a private key from a PEM file.

    This function reads a private key from the specified file path and returns
    a private key object that can be used for signing operations.

    Args:
        private_key_path: The absolute or relative path to the private key file
                          (e.g., 'private_key.pem').
    Returns:
        A private key object from the cryptography library (e.g., Ed25519PrivateKey,
        RSAPrivateKey, etc.).
    """
    with open(private_key_path, "rb") as key_file:
        key_bytes = key_file.read()

    return serialization.load_pem_private_key(key_bytes, password=None)


def private_key_type(private_key: PrivateKeyTypes) -> str:
    """Return the type of the private key as a string."""
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        return "Ed25519"
    if isinstance(private_key, rsa.RSAPrivateKey):
        return "RSA"
    return "Unknown"


def load_public_key(file_path: str) -> PublicKeyTypes:
    """
    Loads a public key from a PEM-formatted file.

    This function reads a public key from the specified file path and returns
    a public key object that can be used for operations like signature
    verification.

    Args:
        file_path: The absolute or relative path to the public key file
                   (e.g., 'public_key.pub' or 'user.pem').

    Returns:
        A public key object from the cryptography library (e.g., Ed25519PublicKey,
        RSAPublicKey, etc.).

    Raises:
        FileNotFoundError: If the file at the specified path does not exist.
        ValueError: If the file content is not a valid PEM-encoded public key
                    or is malformed.
        UnsupportedAlgorithm: If the key type is not supported by the backend.
    """
    with open(file_path, "rb") as key_file:
        key_bytes = key_file.read()

    return serialization.load_pem_public_key(key_bytes)


def public_key_type(public_key: PublicKeyTypes) -> str:
    """Return the type of the public key as a string."""
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        return "Ed25519"
    if isinstance(public_key, rsa.RSAPublicKey):
        return "RSA"
    return "Unknown"


def _create_signature_payload(file_hash: str, creator_uuid: str, algorithm: str) -> str:
    """Create a canonical payload for signing that includes critical metadata.

    This ensures that the signature covers not just the file hash, but also
    the creator UUID and algorithm, preventing tampering with these fields.

    Args:
        file_hash: SHA-256 hash of the file.
        creator_uuid: UUID of the creator as a string.
        algorithm: Signature algorithm used.

    Returns:
        Canonical JSON string with sorted keys and compact separators.
    """
    payload = {"file_hash": file_hash, "creator_uuid": creator_uuid, "algorithm": algorithm}
    # Use sorted keys and compact separators for canonical representation
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


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

    The signature covers the file hash, creator UUID, and algorithm to prevent
    tampering with these critical metadata fields.

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
    if not exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Compute the SHA-256 hash of the file
    file_hash = _compute_file_hash(filepath)

    # Create canonical payload that includes critical metadata
    creator_uuid_str = str(creator_uuid)
    payload = _create_signature_payload(file_hash, creator_uuid_str, algorithm)

    # Load the private key
    private_key_bytes = private_key_pem.encode("utf-8")

    if algorithm == "Ed25519":
        try:
            private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
            if not isinstance(private_key, ed25519.Ed25519PrivateKey):
                raise ValueError("Private key is not an Ed25519 key")
        except Exception as e:
            raise ValueError(f"Failed to load Ed25519 private key: {e}") from e

        # Sign the canonical payload
        signature_bytes = private_key.sign(payload.encode("utf-8"))

    elif algorithm == "RSA":
        try:
            private_key = serialization.load_pem_private_key(private_key_bytes, password=None)
            if not isinstance(private_key, rsa.RSAPrivateKey):
                raise ValueError("Private key is not an RSA key")
        except Exception as e:
            raise ValueError(f"Failed to load RSA private key: {e}") from e

        # Sign the canonical payload using RSA with PSS padding
        signature_bytes = private_key.sign(
            payload.encode("utf-8"),
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
        "creator_uuid": creator_uuid_str,
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


def load_signature_data(path: str) -> dict[str, Any]:
    """Load and validate signature metadata from a .sig JSON file.

    Args:
        path: Path to the .sig JSON file.
    Returns:
        Dictionary containing signature metadata with the structure:
        {
            "file_hash": str,  # sha256 hexdigest
            "signature": str,  # b64 encoded
            "algorithm": str,
            "creator_uuid": str
        }
    Raises:
        FileNotFoundError: If the signature file does not exist.
        ValueError: If required fields are missing in the signature file.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = load(f)

    required_fields = ["file_hash", "signature", "algorithm", "creator_uuid"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field in signature file: {field}")
    return data


def verify_file_signature(  # pylint: disable=too-many-branches,too-many-locals
    filepath: str,
    public_key_pem: str,
    sig_filepath: str | None = None,
) -> bool:
    """Verify a file's signature using a detached signature file.

    The verification checks both the file integrity and that the signature
    covers the file hash, creator UUID, and algorithm to prevent tampering.

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
    if not exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if sig_filepath is None:
        sig_filepath = f"{filepath}.sig"

    if not exists(sig_filepath):
        raise FileNotFoundError(f"Signature file not found: {sig_filepath}")

    sig_data = load_signature_data(sig_filepath)

    stored_hash = sig_data["file_hash"]
    signature_b64 = sig_data["signature"]
    algorithm = sig_data["algorithm"]
    creator_uuid_str = sig_data["creator_uuid"]

    # Compute current file hash
    current_hash = _compute_file_hash(filepath)

    # Verify hash matches
    if current_hash != stored_hash:
        raise HashMismatchError(f"File hash mismatch. Expected: {stored_hash}, Got: {current_hash}")

    # Create the same canonical payload that was signed
    payload = _create_signature_payload(stored_hash, creator_uuid_str, algorithm)

    # Decode signature with strict validation
    try:
        signature_bytes = base64.b64decode(signature_b64, validate=True)
    except binascii.Error as e:
        raise ValueError("Failed to decode signature: invalid base64 encoding") from e

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
            public_key.verify(signature_bytes, payload.encode("utf-8"))
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
                payload.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        except CryptographyInvalidSignature as e:
            raise InvalidSignatureError(
                f"Signature verification failed (algorithm: {algorithm})"
            ) from e
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return True


def dump_signed_json(data: dict | list, fullpath: str) -> None:
    """
    Dump a signed JSON file with canonical formatting and embedded signature.

    The function serializes the provided data (dict or list) to JSON using sorted keys and
    compact separators
    to ensure a canonical representation. It then generates a digital signature over the canonical
    JSON payload,
    including critical metadata such as the creator UUID and signature algorithm.
    The resulting file includes
    both the signed data and the signature, allowing for later verification of integrity and
    authenticity.

    Args:
        data: The data to serialize and sign (dict or list).
        fullpath: The path to the output JSON file.

    Raises:
        ValueError: If the file size exceeds the JSON_FILESIZE_LIMIT.
        InvalidSignatureError: If signing fails.

    Note:
        The implementation must ensure that the signature covers both the data and
        relevant metadata,
        and that the file is written in a format suitable for later verification.
    """
    with open(fullpath, "w", encoding="utf-8") as f:
        dump(data, f, indent=2, sort_keys=True, ensure_ascii=True)
    # Prevents continuing with a file we can't read
    _file_size_limit(fullpath, JSON_FILESIZE_LIMIT)

    # Load the private key for signing
    private_key = load_private_key(PRIVATE_KEY_FILE)
    private_key_type_str = private_key_type(private_key)
    private_key_str = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    # TODO:
    #   1. Encrypted private key should be default, with password retrieval mechanism.
    #   2. Need UUID associated with the private key for creator_uuid.
    # For now we use the SHAPEDSUNDEW9_UUID as a placeholder.
    sig_file_path = sign_file(
        fullpath, private_key_str, SHAPEDSUNDEW9_UUID, algorithm=private_key_type_str
    )

    # Make sure the signature file is created and valid
    if not exists(sig_file_path):
        raise InvalidSignatureError(f"Failed to create signature file: {sig_file_path}")

    # TODO: Determine the right public key to use for verification
    public_key = load_public_key(join(PUBLIC_KEY_FOLDER, str(SHAPEDSUNDEW9_UUID) + ".pub"))
    public_key_str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    if not verify_file_signature(fullpath, public_key_str, sig_filepath=sig_file_path):
        raise InvalidSignatureError(f"Signature verification failed for file: {fullpath}")


def _file_size_limit(fullpath: str, limit: int = 2**30) -> int:
    """Check if the file size is within the limit."""
    size = getsize(fullpath)
    if size > limit:
        raise ValueError(f"File {fullpath} size {size} exceeds limit {limit}.")
    return size


def load_signed_json(fullpath: str) -> dict | list:
    """Load a signed JSON file.

    Validate that creator UUID and signature is correct and return the JSON object.
    """
    _file_size_limit(fullpath, JSON_FILESIZE_LIMIT)

    # TODO: Try public keys with the UUID until we find one that works
    public_key = load_public_key(join(PUBLIC_KEY_FOLDER, str(SHAPEDSUNDEW9_UUID) + ".pub"))
    public_key_str = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    if not verify_file_signature(fullpath, public_key_str, sig_filepath=f"{fullpath}.sig"):
        raise InvalidSignatureError(f"Signature verification failed for file: {fullpath}")
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
