"""Codon development loader.

This module assists codon development when codon signatures change frequently.
It loads codon and meta-codon definitions from JSON files and finds codons that
match a given list of input types, output types, and the codon name stored in
the codon's metadata. When a match is found, the codon's signature is returned
as a bytes object.

Note: JSON files should be loaded with the security module's helper (e.g.
load_json_file_list) or an equivalent routine to ensure the expected structure and
validation. The codon and metacodon data is cached so that repeated accesses are swift
but this has a memory overhead.
"""

from collections.abc import Sequence
from os.path import dirname, join
from typing import Any

from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.security import load_signed_json_list

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)

# Default paths to codon JSON files
DEFAULT_CODON_PATHS: tuple[str, ...] = (
    join(dirname(__file__), "..", "..", "egppy", "egppy", "data", "codons.json"),
    join(dirname(__file__), "..", "..", "egppy", "egppy", "data", "meta_codons.json"),
)

# Cache for loaded codons indexed by (input_types, output_types, name)
_codon_cache: dict[tuple[tuple[str, ...], tuple[str, ...], str], bytes] = {}

# Track which files have been loaded
_loaded_files: set[str] = set()


def _load_codons_from_files(file_paths: Sequence[str]) -> None:
    """Load codons from JSON files into the cache.

    This function loads codon definitions from the specified JSON files and populates
    the internal cache. Each codon is indexed by its input types, output types, and name
    from the metadata.

    Args:
        file_paths: Sequence of file paths to load codons from.

    Raises:
        FileNotFoundError: If a file does not exist.
        ValueError: If the JSON structure is invalid or required fields are missing.
    """
    for file_path in file_paths:
        if file_path in _loaded_files:
            if _LOG_DEBUG:
                _logger.debug("Skipping already loaded file: %s", file_path)
            continue

        if _LOG_DEBUG:
            _logger.debug("Loading codons from: %s", file_path)

        codons_list: list[dict[str, Any]] = load_signed_json_list(file_path)

        for codon in codons_list:
            # Extract required fields
            input_types = tuple(codon.get("input_types", []))
            output_types = tuple(codon.get("output_types", []))

            # Extract the name from metadata
            # Structure: meta_data -> function -> python3 -> "0" -> name
            meta_data = codon.get("meta_data", {})
            function_data = meta_data.get("function", {})
            python3_data = function_data.get("python3", {})
            variant_0 = python3_data.get("0", {})
            name = variant_0.get("name", "")

            if not name:
                if _LOG_DEBUG:
                    _logger.debug(
                        "Skipping codon without name: signature=%s",
                        codon.get("signature", "N/A"),
                    )
                continue

            # Extract signature as bytes
            signature_str = codon.get("signature")
            if not signature_str:
                if _LOG_DEBUG:
                    _logger.debug("Skipping codon without signature: name=%s", name)
                continue

            signature = bytes.fromhex(signature_str)

            # Create cache key
            cache_key = (input_types, output_types, name)

            # Store in cache (newer entries overwrite older ones)
            _codon_cache[cache_key] = signature

            if _LOG_DEBUG:
                _logger.debug(
                    "Cached codon: name=%s, inputs=%s, outputs=%s, signature=%s...",
                    name,
                    input_types,
                    output_types,
                    signature_str[:16],
                )

        _loaded_files.add(file_path)

        if _LOG_DEBUG:
            _logger.debug("Loaded %d codons from %s", len(codons_list), file_path)


def clear_cache() -> None:
    """Clear the codon cache and loaded files tracking.

    This function clears all cached codon data and resets the loaded files set.
    Useful for testing or when codon files have been modified and need to be reloaded.
    """
    _codon_cache.clear()
    _loaded_files.clear()

    if _LOG_DEBUG:
        _logger.debug("Codon cache cleared")


def find_codon_signature(
    input_types: Sequence[str],
    output_types: Sequence[str],
    name: str,
    file_paths: Sequence[str] | None = None,
) -> bytes:
    """Find a codon signature matching the specified criteria.

    This function searches for a codon that matches the given input types, output types,
    and name. The search is performed in the cached codon data, which is loaded from
    JSON files on first access or when new file paths are provided.

    Args:
        input_types: Sequence of input type names (e.g., ["int", "str"]).
        output_types: Sequence of output type names (e.g., ["bool"]).
        name: The codon name as stored in meta_data -> function -> python3 -> "0" -> name.
        file_paths: Optional sequence of file paths to load codons from. If None,
                   uses DEFAULT_CODON_PATHS.

    Returns:
        The codon signature as bytes.

    Raises:
        FileNotFoundError: If a specified file does not exist.
        ValueError: If the JSON structure is invalid or required fields are missing
                    or the codon is not found.

    Example:
        >>> sig = find_codon_signature(["int", "int"], ["int"], "add")
        >>> if sig:
        ...     print(f"Found signature: {sig.hex()}")
    """
    # Use default paths if none provided
    if file_paths is None:
        file_paths = DEFAULT_CODON_PATHS

    # Load codons from files if not already loaded
    _load_codons_from_files(file_paths)

    # Create lookup key
    cache_key = (tuple(input_types), tuple(output_types), name)

    # Look up in cache
    signature = _codon_cache.get(cache_key)

    if signature is None and _LOG_DEBUG:
        _logger.debug(
            "Codon not found: name=%s, inputs=%s, outputs=%s", name, input_types, output_types
        )
        raise ValueError(
            f"Codon not found: name={name}, inputs={input_types}, outputs={output_types}"
        )

    assert signature is not None  # For type checkers
    return signature
