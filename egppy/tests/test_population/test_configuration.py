"""Test population configuration."""
from datetime import datetime
from typing import Callable
from unittest import TestCase
from uuid import UUID, uuid4
from egppy.gc_graph.ep_type import asint
from egppy.population.configuration import PopulationConfig, PopulationsConfig


def xf(_: Callable) -> float:
    """Dummy survivability / fitness function."""
    return 1.0


class TestPopulationConfig(TestCase):
    """Test the population configuration class."""

    def test_init(self):
        """Test the initialization of the class."""
        config = PopulationConfig(
            uid = 7,
            problem = "1"*64,
            worker_id = str(uuid4()),
            size = 10,
            inputs = ['int', 'str', 'bool'],
            outputs = ['int', 'str', 'bool'],
            ordered_interface_hash = "1"*16,
            unordered_interface_hash = "e"*16,
            name = "test",
            description = "test",
            meta_data = '{"test": "test"}',
            created = datetime.now().isoformat(),
            updated = datetime.now().isoformat(),
            survivability_function = xf,
            fitness_function = xf
        )
        self.assertEqual(config.uid, 7)
        self.assertEqual(config.problem, bytes.fromhex("1"*64))
        self.assertIsInstance(config.worker_id, UUID)
        self.assertEqual(config.size, 10)
        self.assertEqual(config.inputs, tuple(asint(x) for x in ['int', 'str', 'bool']))
        self.assertEqual(config.outputs, tuple(asint(x) for x in ['int', 'str', 'bool']))
        self.assertEqual(config.ordered_interface_hash, bytes.fromhex("1"*16))
        self.assertEqual(config.unordered_interface_hash, bytes.fromhex("e"*16))
        self.assertEqual(config.name, "test")
        self.assertEqual(config.description, "test")
        self.assertEqual(config.meta_data, '{"test": "test"}')
        self.assertIsInstance(config.created, datetime)
        self.assertIsInstance(config.updated, datetime)
        self.assertEqual(config.survivability_function, xf)
        self.assertEqual(config.fitness_function, xf)

    def test_to_json(self) -> None:
        """Test the to_json method."""
        config = PopulationConfig(
            uid = 7,
            problem = "1"*64,
            worker_id = str(uuid4()),
            size = 10,
            inputs = ['int', 'str', 'bool'],
            outputs = ['int', 'str', 'bool'],
            ordered_interface_hash = "1"*16,
            unordered_interface_hash = "e"*16,
            name = "test",
            description = "test",
            meta_data = '{"test": "test"}',
            created = datetime.now().isoformat(),
            updated = datetime.now().isoformat(),
            survivability_function = xf,
            fitness_function = xf
        )
        self.assertEqual(config.to_json(), PopulationConfig(**config.to_json()).to_json())


class TestPopulationsConfig(TestCase):
    """Test the populations configuration class."""

    def test_init(self):
        """Test the initialization of the class."""

        config = PopulationsConfig(
            worker_id = str(uuid4()),
            configs = [
                PopulationConfig(
                    uid = 7,
                    problem = "1"*64,
                    worker_id = str(uuid4()),
                    size = 10,
                    inputs = ['int', 'str', 'bool'],
                    outputs = ['int', 'str', 'bool'],
                    ordered_interface_hash = "1"*16,
                    unordered_interface_hash = "e"*16,
                    name = "test",
                    description = "test",
                    meta_data = '{"test = "test"}',
                    created = datetime.now().isoformat(),
                    updated = datetime.now().isoformat(),
                    survivability_function = xf,
                    fitness_function = xf
                )
            ]
        )
        self.assertIsInstance(config.worker_id, UUID)
        self.assertEqual(len(config.configs), 1)
        self.assertIsInstance(config.configs[0], PopulationConfig)
