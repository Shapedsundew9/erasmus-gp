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
RSHIFT_SIG = bytes.fromhex("6871b4bdbc8bc0f780c0eb46b32b5630fc4cb2914bdf12b4135dc34b1f8a6b4a")
