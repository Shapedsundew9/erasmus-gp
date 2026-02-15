"""Unit tests for the egppy.physics.runtime_context module.

Tests cover RuntimeContext initialization, slot enforcement,
default values, and parent attribute.
"""

import unittest
from unittest.mock import MagicMock
from uuid import uuid4

from egpcommon.common import ANONYMOUS_CREATOR
from egppy.physics.runtime_context import RuntimeContext


class TestRuntimeContext(unittest.TestCase):
    """Test the RuntimeContext class."""

    def _make_context(self, **kwargs) -> RuntimeContext:
        """Create a RuntimeContext with a mocked GenePoolInterface."""
        defaults = {"gpi": MagicMock()}
        defaults.update(kwargs)
        return RuntimeContext(**defaults)

    def test_init_defaults(self) -> None:
        """RuntimeContext uses correct defaults for optional params."""
        gpi = MagicMock()
        ctx = RuntimeContext(gpi=gpi)
        self.assertIs(ctx.gpi, gpi)
        self.assertEqual(ctx.creator, ANONYMOUS_CREATOR)
        self.assertIsNone(ctx.debug_data)
        self.assertIsNone(ctx.parent)

    def test_init_custom_creator(self) -> None:
        """RuntimeContext accepts a custom creator UUID."""
        creator = uuid4()
        ctx = self._make_context(creator=creator)
        self.assertEqual(ctx.creator, creator)

    def test_init_debug_data(self) -> None:
        """RuntimeContext stores debug_data dict."""
        data = {"step": 1, "result": "ok"}
        ctx = self._make_context(debug_data=data)
        self.assertEqual(ctx.debug_data, data)

    def test_slots_enforced(self) -> None:
        """RuntimeContext uses __slots__; arbitrary attributes are rejected."""
        ctx = self._make_context()
        with self.assertRaises(AttributeError):
            # pylint: disable = assigning-non-slot
            ctx.nonexistent_attr = "fail"  # type: ignore[attr-defined]

    def test_parent_initially_none(self) -> None:
        """parent starts as None."""
        ctx = self._make_context()
        self.assertIsNone(ctx.parent)

    def test_parent_settable(self) -> None:
        """parent can be set to a GC mock."""
        ctx = self._make_context()
        mock_gc = MagicMock()
        ctx.parent = mock_gc
        self.assertIs(ctx.parent, mock_gc)


if __name__ == "__main__":
    unittest.main()
