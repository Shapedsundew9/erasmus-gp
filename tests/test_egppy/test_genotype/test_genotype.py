"""Unit tests for the egppy.genotype.genotype module.

Tests cover the StateABC, State, and Genotype classes including
initialization, slot enforcement, energy callback, and execution.
"""

import unittest
from typing import Any

from numpy import double, int64

from egppy.genotype.genotype import DOUBLE_ZERO, INT64_65536, INT64_ZERO, Genotype, State, StateABC


class TestConstants(unittest.TestCase):
    """Test module-level constants."""

    def test_double_zero(self) -> None:
        """DOUBLE_ZERO is a numpy double equal to 0.0."""
        self.assertEqual(float(DOUBLE_ZERO), 0.0)
        self.assertIsInstance(DOUBLE_ZERO, double)

    def test_int64_zero(self) -> None:
        """INT64_ZERO is a numpy int64 equal to 0."""
        self.assertEqual(int(INT64_ZERO), 0)
        self.assertIsInstance(INT64_ZERO, int64)

    def test_int64_65536(self) -> None:
        """INT64_65536 is a numpy int64 equal to 2**16."""
        self.assertEqual(int(INT64_65536), 2**16)
        self.assertIsInstance(INT64_65536, int64)


class TestState(unittest.TestCase):
    """Test the State class (concrete list-based StateABC implementation)."""

    def test_state_is_list(self) -> None:
        """State inherits from list."""
        state = State()
        self.assertIsInstance(state, list)

    def test_state_is_state_abc(self) -> None:
        """State inherits from StateABC."""
        state = State()
        self.assertIsInstance(state, StateABC)

    def test_state_append(self) -> None:
        """State.append adds items."""
        state = State()
        state.append(42)
        self.assertEqual(len(state), 1)
        self.assertEqual(state[0], 42)

    def test_state_getitem(self) -> None:
        """State supports indexed access."""
        state = State([10, 20, 30])
        self.assertEqual(state[1], 20)

    def test_state_setitem(self) -> None:
        """State supports indexed assignment."""
        state = State([10, 20, 30])
        state[1] = 99
        self.assertEqual(state[1], 99)

    def test_state_delitem(self) -> None:
        """State supports indexed deletion."""
        state = State([10, 20, 30])
        del state[1]
        self.assertEqual(len(state), 2)
        self.assertEqual(state[1], 30)

    def test_state_iter(self) -> None:
        """State supports iteration."""
        state = State([1, 2, 3])
        self.assertEqual(list(iter(state)), [1, 2, 3])

    def test_state_len(self) -> None:
        """State supports len()."""
        state = State()
        self.assertEqual(len(state), 0)
        state.append("x")
        self.assertEqual(len(state), 1)


class TestGenotype(unittest.TestCase):
    """Test the Genotype class."""

    @staticmethod
    def _dummy_func(i: tuple) -> tuple:
        """A trivial function for testing."""
        return i

    def _make_genotype(self, **kwargs: Any) -> Genotype:
        """Helper to create a Genotype with default values."""
        defaults: dict[str, Any] = {
            "signature": b"test_sig",
            "func": self._dummy_func,
            "puid": 1,
        }
        defaults.update(kwargs)
        return Genotype(**defaults)

    def test_init_sets_attributes(self) -> None:
        """Genotype.__init__ correctly sets all attributes."""
        sig = b"abc123"
        gt = Genotype(signature=sig, func=self._dummy_func, puid=42)
        self.assertEqual(gt.signature, sig)
        self.assertEqual(gt.func, self._dummy_func)
        self.assertEqual(gt.puid, 42)
        self.assertIsInstance(gt.state, State)
        self.assertIsInstance(gt.memory, State)
        self.assertEqual(int(gt.energy), int(INT64_65536))
        self.assertEqual(float(gt.fitness), 0.0)
        self.assertEqual(float(gt.survivability), 0.0)
        self.assertIsNone(gt.problem_meta_data)

    def test_slots_enforced(self) -> None:
        """Genotype uses __slots__; arbitrary attributes are rejected."""
        gt = self._make_genotype()
        with self.assertRaises(AttributeError):
            # pylint: disable = assigning-non-slot
            gt.nonexistent_attr = "should fail"  # type: ignore[attr-defined]

    def test_energy_callback(self) -> None:
        """energy_cb adjusts energy and returns the new value."""
        gt = self._make_genotype()
        initial = int(gt.energy)
        result = gt.energy_cb(int64(-100))
        self.assertEqual(int(result), initial - 100)
        self.assertEqual(int(gt.energy), initial - 100)

    def test_energy_callback_accumulates(self) -> None:
        """Repeated energy_cb calls accumulate correctly."""
        gt = self._make_genotype()
        gt.energy_cb(int64(-10))
        gt.energy_cb(int64(-20))
        expected = int(INT64_65536) - 10 - 20
        self.assertEqual(int(gt.energy), expected)

    def test_execute_returns_func_result(self) -> None:
        """Genotype.execute delegates to func."""
        gt = self._make_genotype()
        result = gt.execute((1, 2, 3))
        self.assertEqual(result, (1, 2, 3))

    def test_execute_dead_individual(self) -> None:
        """Genotype.execute asserts energy > 0."""
        gt = self._make_genotype()
        gt.energy = INT64_ZERO
        with self.assertRaises(AssertionError):
            gt.execute((1,))

    def test_problem_meta_data_settable(self) -> None:
        """problem_meta_data can be set to any value."""
        gt = self._make_genotype()
        gt.problem_meta_data = {"key": "value"}
        self.assertEqual(gt.problem_meta_data, {"key": "value"})

    def test_state_and_memory_independent(self) -> None:
        """state and memory are separate State instances."""
        gt = self._make_genotype()
        gt.state.append("s")
        gt.memory.append("m")
        self.assertEqual(list(gt.state), ["s"])
        self.assertEqual(list(gt.memory), ["m"])


if __name__ == "__main__":
    unittest.main()
