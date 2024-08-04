"""Tests for egp-seed."""

from egpseed import _generate


def test_initialize() -> None:
    """Generate the types & codons.

    cp ~/Projects/egp-seed/data/ep_types.json ~/Projects/egp-types/egp_types/data/
    cp ~/Projects/egp-seed/data/codons.json ~/Projects/egp-stores/egp_stores/data/
    """
    _generate("python")


if __name__ == "__main__":
    test_initialize()
