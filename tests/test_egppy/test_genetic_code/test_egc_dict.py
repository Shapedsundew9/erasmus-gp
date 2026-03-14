"""Unit tests for EGCDict mutable-hash prohibition (WP5).

EGCDict is a mutable builder and MUST NOT be hashable.
"""

import unittest

from egppy.genetic_code.egc_dict import EGCDict


class TestEGCDictHashProhibition(unittest.TestCase):
    """Contract 2: EGCDict Mutable Hash Behavior (WP5).

    Calling hash() on an EGCDict MUST raise TypeError.
    """

    def test_egc_dict_not_hashable(self) -> None:
        """EGCDict must not be hashable."""
        egc = EGCDict()
        with self.assertRaises(TypeError):
            hash(egc)


if __name__ == "__main__":
    unittest.main()
