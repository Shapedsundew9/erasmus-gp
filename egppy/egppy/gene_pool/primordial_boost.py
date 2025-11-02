"""
Primordial boost — initialize simple physical genetic codes.

This module provides helper routines used to "kick start" evolution
by constructing primitive genetic codes and applying basic
selection and mutation operations. It is intended for use during the
early stages of development to save waiting around for chance discoveries.
"""

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.ggc_class_factory import GGCDict
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG

# Initialize the Gene Pool Interface
gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)


# Load the primitive codons from the gene pool
PSQL_PRP_MASK = bytes.fromhex("6ded397736576935846261a9562367785a04dbb32e417f11812518947e5cffff")
PSQL_PRP_COLUMN = bytes.fromhex("964a4445b474efd99d6bcc1925b0ed352e4918858bbee85e62c64ba8720150fc")
PSQL_BITWISE_AND = bytes.fromhex("b52115998c3673240f15016b29f67d88c32665d388665ebf50c6e1262faf5af5")
PSQL_ORDERBY_RND = bytes.fromhex("737815bade001855279f18c3c90f549e60e871d3ff7954d7dde5ff39f9d86ece")
PSQL_WHERE = bytes.fromhex("0c179e741362dfd6802acbb0fbb880817c31ff12f45e725e918b4771682bb5b1")
GPI_SELECT_GC = bytes.fromhex("4c63c6a4a2c26b619aeca765af5b5d84732f246b0ce4033670862d41e60aa6b5")

PSQL_PRP_MASK_GC = gpi[PSQL_PRP_MASK]
PSQL_PRP_COLUMN_GC = gpi[PSQL_PRP_COLUMN]
PSQL_BITWISE_AND_GC = gpi[PSQL_BITWISE_AND]
PSQL_ORDERBY_RND_GC = gpi[PSQL_ORDERBY_RND]
PSQL_WHERE_GC = gpi[PSQL_WHERE]
GPI_SELECT_GC_GC = gpi[GPI_SELECT_GC]
