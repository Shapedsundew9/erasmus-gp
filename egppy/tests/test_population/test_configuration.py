"""Test population configuration."""

from datetime import datetime
from typing import Callable
from unittest import TestCase
from uuid import UUID, uuid4

from egppy.gc_graph.end_point.types_def import types_db
from egppy.populations.configuration import PopulationConfig, PopulationsConfig, SourceConfig


def xf(_: Callable) -> float:
    """Dummy survivability / fitness function."""
    return 1.0


class TestSourceConfig(TestCase):
    """Test the source configuration class."""

    def test_init_best(self):
        """Test the initialization of the BEST source."""
        config = SourceConfig(source="BEST", scope=127, limit=20, underflow="NEXT")
        self.assertEqual(config.source, "BEST")
        self.assertEqual(config.scope, 127)
        self.assertEqual(config.limit, 20)
        self.assertEqual(config.underflow, "NEXT")

    def test_init_diverse(self):
        """Test the initialization of the DIVERSE source."""
        config = SourceConfig(
            source="DIVERSE",
            scope=127,
            limit=20,
            underflow="NEXT",
            minimum_distance=4,
            fitness_threshold=0.5,
            novelty_threshold=0.5,
        )
        self.assertEqual(config.source, "DIVERSE")
        self.assertEqual(config.scope, 127)
        self.assertEqual(config.limit, 20)
        self.assertEqual(config.underflow, "NEXT")
        self.assertEqual(config.minimum_distance, 4)
        self.assertEqual(config.fitness_threshold, 0.5)
        self.assertEqual(config.novelty_threshold, 0.5)

    def test_init_related(self):
        """Test the initialization of the RELATED source."""
        config = SourceConfig(
            source="RELATED",
            scope=127,
            limit=20,
            underflow="NEXT",
            maximum_problem_distance=4,
            minimum_distance=4,
            tolerence=10,
        )
        self.assertEqual(config.source, "RELATED")
        self.assertEqual(config.scope, 127)
        self.assertEqual(config.limit, 20)
        self.assertEqual(config.underflow, "NEXT")
        self.assertEqual(config.maximum_problem_distance, 4)
        self.assertEqual(config.minimum_distance, 4)
        self.assertEqual(config.tolerence, 10)

    def test_init_unrelated(self):
        """Test the initialization of the UNRELATED source."""
        config = SourceConfig(
            source="UNRELATED",
            scope=127,
            limit=20,
            underflow="NEXT",
            minimum_problem_distance=5,
            minimum_distance=4,
            tolerence=10,
        )
        self.assertEqual(config.source, "UNRELATED")
        self.assertEqual(config.scope, 127)
        self.assertEqual(config.limit, 20)
        self.assertEqual(config.underflow, "NEXT")
        self.assertEqual(config.minimum_problem_distance, 5)
        self.assertEqual(config.minimum_distance, 4)
        self.assertEqual(config.tolerence, 10)

    def test_init_spontaneous(self):
        """Test the initialization of the SPONTANEOUS source."""
        config = SourceConfig(
            source="SPONTANEOUS",
            scope=127,
            limit=20,
            underflow="NEXT",
            sse_limit=100,
            tolerence=100,
            minimum_generation=0,
            maximum_generation=0,
        )
        self.assertEqual(config.source, "SPONTANEOUS")
        self.assertEqual(config.scope, 127)
        self.assertEqual(config.limit, 20)
        self.assertEqual(config.underflow, "NEXT")
        self.assertEqual(config.sse_limit, 100)
        self.assertEqual(config.tolerence, 100)

    def test_invalid_source(self):
        """Test the initialization with an invalid source."""
        with self.assertRaises(AssertionError):
            SourceConfig(source="INVALID")

    def test_to_json(self):
        """Test the to_json method."""
        sources = [
            {
                "source": "BEST",
                "scope": 127,
                "limit": 20,
                "underflow": "NEXT",
            },
            {
                "source": "DIVERSE",
                "scope": 127,
                "limit": 20,
                "underflow": "NEXT",
                "minimum_distance": 4,
                "fitness_threshold": 0.5,
                "novelty_threshold": 0.5,
            },
            {
                "source": "RELATED",
                "scope": 127,
                "limit": 20,
                "underflow": "NEXT",
                "maximum_problem_distance": 4,
                "minimum_distance": 4,
                "tolerence": 10,
            },
            {
                "source": "UNRELATED",
                "scope": 127,
                "limit": 20,
                "underflow": "NEXT",
                "minimum_problem_distance": 5,
                "minimum_distance": 4,
                "tolerence": 10,
            },
            {
                "source": "SPONTANEOUS",
                "scope": 127,
                "limit": 20,
                "underflow": "NEXT",
                "sse_limit": 100,
                "tolerence": 100,
                "minimum_generation": 0,
                "maximum_generation": 0,
            },
        ]

        for source_config in sources:
            config = SourceConfig(**source_config)
            self.assertEqual(config.to_json(), source_config)


class TestPopulationConfig(TestCase):
    """Test the population configuration class."""

    def test_init(self):
        """Test the initialization of the class."""
        config = PopulationConfig(
            uid=7,
            problem="1" * 64,
            worker_id=str(uuid4()),
            inputs=["int", "str", "bool"],
            outputs=["int", "str", "bool"],
            ordered_interface_hash="1" * 16,
            unordered_interface_hash="e" * 16,
            name="test",
            description="test",
            meta_data='{"test": "test"}',
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            survivability_function=xf,
            fitness_function=xf,
        )
        self.assertEqual(config.uid, 7)
        self.assertEqual(config.problem, bytes.fromhex("1" * 64))
        self.assertIsInstance(config.worker_id, UUID)
        self.assertEqual(config.inputs, tuple((types_db[x],) for x in ["int", "str", "bool"]))
        self.assertEqual(config.outputs, tuple((types_db[x],) for x in ["int", "str", "bool"]))
        self.assertEqual(config.ordered_interface_hash, bytes.fromhex("1" * 16))
        self.assertEqual(config.unordered_interface_hash, bytes.fromhex("e" * 16))
        self.assertEqual(config.name, "test")
        self.assertEqual(config.description, "test")
        self.assertEqual(config.meta_data, '{"test": "test"}')
        self.assertIsInstance(config.created, datetime)
        self.assertIsInstance(config.updated, datetime)
        self.assertEqual(config.survivability_function, xf)
        self.assertEqual(config.fitness_function, xf)

    def test_to_json(self) -> None:
        """Test the to_json method."""
        _ = PopulationConfig(
            uid=7,
            problem="1" * 64,
            worker_id=str(uuid4()),
            inputs=["int", "str", "bool"],
            outputs=["int", "str", "bool"],
            ordered_interface_hash="1" * 16,
            unordered_interface_hash="e" * 16,
            name="test",
            description="test",
            meta_data='{"test": "test"}',
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            survivability_function=xf,
            fitness_function=xf,
        )
        # FIXME: This test is failing as the survivability_function and fitness_function
        # are not serializable. We need to fix this.
        # self.assertEqual(config.to_json(), PopulationConfig(**config.to_json()).to_json())


class TestPopulationsConfig(TestCase):
    """Test the populations configuration class."""

    def test_init(self):
        """Test the initialization of the class."""

        config = PopulationsConfig(
            worker_id=str(uuid4()),
            configs=[
                PopulationConfig(
                    uid=7,
                    problem="1" * 64,
                    worker_id=str(uuid4()),
                    inputs=["int", "str", "bool"],
                    outputs=["int", "str", "bool"],
                    ordered_interface_hash="1" * 16,
                    unordered_interface_hash="e" * 16,
                    name="test",
                    description="test",
                    meta_data='{"test = "test"}',
                    created=datetime.now().isoformat(),
                    updated=datetime.now().isoformat(),
                    survivability_function=xf,
                    fitness_function=xf,
                )
            ],
        )
        self.assertIsInstance(config.worker_id, UUID)
        self.assertEqual(len(config.configs), 1)
        self.assertIsInstance(config.configs[0], PopulationConfig)
