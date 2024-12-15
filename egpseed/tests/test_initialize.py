"""Tests for egp-seed."""

from egpseed.initialize import _generate


def test_initialize() -> None:
    """Generate the types & codons."""
    _generate("python")


if __name__ == "__main__":
    test_initialize()
