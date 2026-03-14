"""Tests for worker initial generation setup."""

import unittest
from unittest.mock import MagicMock, patch

from egpdb.configuration import DatabaseConfig
from egpdbmgr.configuration import DBManagerConfig, TableTypes
from egppy.worker.configuration import WorkerConfig
from egppy.worker.init_generation import _gene_pool_db_manager_config, init_generation


class TestInitGenerationConfigMapping(unittest.TestCase):
    """Test worker-to-DB manager configuration mapping."""

    def test_gene_pool_db_manager_config_minimal_mapping(self) -> None:
        """Map worker configuration to minimal gene pool DB manager configuration."""
        worker_config = WorkerConfig(
            databases={
                "pool_db": DatabaseConfig(dbname="pool", host="postgres"),
                "micro_db": DatabaseConfig(dbname="micro", host="postgres"),
            },
            gene_pool="pool_db",
            microbiome="micro_db",
        )

        dbm_config = _gene_pool_db_manager_config(worker_config)

        self.assertIsInstance(dbm_config, DBManagerConfig)
        self.assertEqual(dbm_config.managed_db, "pool_db")
        self.assertEqual(dbm_config.managed_type, TableTypes.POOL)
        self.assertEqual(dbm_config.upstream_dbs, ["micro_db"])
        self.assertEqual(set(dbm_config.databases.keys()), {"pool_db", "micro_db"})

    def test_gene_pool_db_manager_config_omits_duplicate_microbiome(self) -> None:
        """Avoid redundant upstream entry when microbiome matches gene pool."""
        worker_config = WorkerConfig(
            databases={"pool_db": DatabaseConfig(dbname="pool", host="postgres")},
            gene_pool="pool_db",
            microbiome="pool_db",
        )

        dbm_config = _gene_pool_db_manager_config(worker_config)

        self.assertEqual(dbm_config.upstream_dbs, [])


class TestInitGenerationWiring(unittest.TestCase):
    """Test init_generation wiring to GenePoolInterface."""

    @patch("egppy.worker.init_generation.fitness_queue")
    @patch("egppy.worker.init_generation.evolution_queue")
    @patch("egppy.worker.init_generation.GenePoolInterface")
    def test_init_generation_passes_db_manager_config_to_gpi(
        self,
        mock_gpi: MagicMock,
        mock_evolution_queue: MagicMock,
        mock_fitness_queue: MagicMock,
    ) -> None:
        """Create GenePoolInterface with derived DBManagerConfig."""
        worker_config = WorkerConfig(
            databases={"pool_db": DatabaseConfig(dbname="pool", host="postgres")},
            gene_pool="pool_db",
            microbiome="pool_db",
        )

        init_generation(worker_config)

        mock_gpi.assert_called_once()
        call_arg = mock_gpi.call_args.args[0]
        self.assertIsInstance(call_arg, DBManagerConfig)
        self.assertEqual(call_arg.managed_db, "pool_db")
        self.assertEqual(call_arg.managed_type, TableTypes.POOL)
        mock_evolution_queue.assert_called_once_with()
        mock_fitness_queue.assert_called_once_with()
