"""Test the genesis problem."""
from unittest import TestCase
from random import choice
from egppy.problems.genesis import EGP_PROBLEM_CONFIG, THE_END_OF_TIME
from egppy.genotype.genotype import Genotype


class TestGenesis(TestCase):
    """Test the genesis problem."""

    def test_fitness_function(self) -> None:
        """Test the fitness function."""
        def _func() -> bool:
            return choice([True, False])

        phenotype = Genotype(
            signature=b"0293869102836509821346598021360985620396509123049652093465320827",
            func=_func,
            puid=0
        )
        EGP_PROBLEM_CONFIG["fitness_function"]([phenotype])
        self.assertGreaterEqual(float(phenotype.fitness), 0.0)
        self.assertLessEqual(float(phenotype.fitness), 1.0)
        self.assertLessEqual(int(phenotype.energy), 0)
        self.assertLessEqual(phenotype.problem_meta_data.lifespan, THE_END_OF_TIME)
