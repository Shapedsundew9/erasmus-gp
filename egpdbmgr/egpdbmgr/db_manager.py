"""EGP Database Manager.

This module provides the database manager for a EGP database.
The EGP database in question may be for the gene-pool or a genomic-library.
There can only be one DB manager for a database at a time.

The DB Manager is responsible for:
    # Creation of the DB as necessary
    # Creation of tables as necessary
    # Initial population of tables (codons etc.)
    # DB data analytics (profiling data, etc.)
    # DB analytics (connection, query, etc.) logging
    # DB maintenance (e.g. vacuuming, re-indexing etc.)
    # Sync'ing the DB back to higher layer databases (micro-biome --> biome etc.)
    # Pulling data from higher layer databases (biome --> micro-biome etc.)
    # DB backup and restore
    # DB migration (e.g. from one version to another)
"""
