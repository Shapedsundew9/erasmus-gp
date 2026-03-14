"""Test the genesis problem.

Tests cover the LifeForm, Environment, fitness_function, and
EGP_PROBLEM_CONFIG for the genesis simulation.
"""

from random import choice
from unittest import TestCase

from numpy import int64

from egppy.genotype.genotype import INT64_ZERO, Genotype
from egppy.problems.genesis import (
    EGP_PROBLEM_CONFIG,
    ENV_MAX,
    ENV_MIN,
    ENV_SIZE,
    NUTRIENT_LEVEL,
    THE_END_OF_TIME,
    Environment,
    LifeForm,
)


class TestLifeForm(TestCase):
    """Test the LifeForm class."""

    def test_default_position(self) -> None:
        """LifeForm defaults to a random position within bounds."""
        lf = LifeForm()
        self.assertGreaterEqual(lf.x, ENV_MIN)
        self.assertLessEqual(lf.x, ENV_MAX)
        self.assertGreaterEqual(lf.y, ENV_MIN)
        self.assertLessEqual(lf.y, ENV_MAX)

    def test_explicit_position(self) -> None:
        """LifeForm accepts explicit x, y coordinates."""
        lf = LifeForm(x=100, y=200)
        self.assertEqual(lf.x, 100)
        self.assertEqual(lf.y, 200)

    def test_initial_energy(self) -> None:
        """LifeForm starts with 2**16 energy."""
        lf = LifeForm()
        self.assertEqual(int(lf.energy), 2**16)

    def test_energy_callback(self) -> None:
        """LifeForm energy_cb modifies and returns energy."""
        lf = LifeForm()
        initial = int(lf.energy)
        result = lf.energy_cb(int64(-50))
        self.assertEqual(int(result), initial - 50)
        self.assertEqual(int(lf.energy), initial - 50)

    def test_action_returns_bool(self) -> None:
        """LifeForm.action returns a boolean."""
        lf = LifeForm()
        result = lf.action()
        self.assertIsInstance(result, bool)

    def test_move_stays_in_bounds(self) -> None:
        """LifeForm.move keeps position within environment limits."""
        lf = LifeForm(x=ENV_MIN, y=ENV_MIN)
        for _ in range(100):
            lf.move()
        self.assertGreaterEqual(lf.x, ENV_MIN)
        self.assertLessEqual(lf.x, ENV_MAX)
        self.assertGreaterEqual(lf.y, ENV_MIN)
        self.assertLessEqual(lf.y, ENV_MAX)

    def test_update_decrements_energy(self) -> None:
        """LifeForm.update decrements energy by at least TIME_COST."""
        lf = LifeForm()
        initial = int(lf.energy)
        lf.update(INT64_ZERO)
        self.assertLess(int(lf.energy), initial)

    def test_lifeform_dies_when_energy_depleted(self) -> None:
        """LifeForm dies when energy reaches zero."""
        lf = LifeForm()
        lf.energy = int64(1)
        alive = lf.update(INT64_ZERO)
        self.assertFalse(alive)


class TestEnvironment(TestCase):
    """Test the Environment class."""

    def test_default_construction(self) -> None:
        """Environment creates 100 default life forms."""
        env = Environment()
        self.assertGreater(len(env.alive), 0)
        self.assertEqual(len(env.dead), 0)
        self.assertEqual(env.num_ticks, 0)

    def test_custom_lifeforms(self) -> None:
        """Environment accepts a custom list of life forms."""
        lfs = [LifeForm(ENV_SIZE // 2, ENV_SIZE // 2)]
        env = Environment(lfs=lfs)
        self.assertEqual(len(env.alive), 1)

    def test_nutrients_initialized(self) -> None:
        """Environment nutrients grid is initialized to NUTRIENT_LEVEL."""
        env = Environment(lfs=[LifeForm()])
        self.assertEqual(env.nutrients[0, 0], NUTRIENT_LEVEL)

    def test_tick_increments(self) -> None:
        """One tick increments num_ticks by 1."""
        env = Environment(lfs=[LifeForm()])
        env.tick()
        self.assertEqual(env.num_ticks, 1)

    def test_short_run(self) -> None:
        """Environment.run with a small tick limit terminates."""
        lf = LifeForm(ENV_SIZE // 2, ENV_SIZE // 2)
        env = Environment(lfs=[lf])
        env.run(tick_limit=10)
        self.assertLessEqual(env.num_ticks, 10)


class TestFitnessFunction(TestCase):
    """Test the fitness_function and EGP_PROBLEM_CONFIG."""

    def test_fitness_function(self) -> None:
        """Test the fitness function sets fitness in [0, 1]."""

        def _func() -> bool:
            return choice([True, False])

        phenotype = Genotype(
            signature=b"0293869102836509821346598021360985620396509123049652093465320827",
            func=_func,
            puid=0,
        )
        EGP_PROBLEM_CONFIG["fitness_function"]([phenotype])
        self.assertGreaterEqual(float(phenotype.fitness), 0.0)
        self.assertLessEqual(float(phenotype.fitness), 1.0)
        self.assertLessEqual(int(phenotype.energy), 0)
        self.assertLessEqual(phenotype.problem_meta_data.lifespan, THE_END_OF_TIME)

    def test_config_has_required_keys(self) -> None:
        """EGP_PROBLEM_CONFIG contains all required keys."""
        for key in ("inputs", "outputs", "fitness_function", "survivability_function"):
            self.assertIn(key, EGP_PROBLEM_CONFIG)

    def test_config_outputs(self) -> None:
        """EGP_PROBLEM_CONFIG outputs is ['bool']."""
        self.assertEqual(EGP_PROBLEM_CONFIG["outputs"], ["bool"])

    def test_config_inputs_empty(self) -> None:
        """EGP_PROBLEM_CONFIG inputs is empty."""
        self.assertEqual(EGP_PROBLEM_CONFIG["inputs"], [])
