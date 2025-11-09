"""
Primordial boost — initialize simple physical genetic codes.

This module provides helper routines used to "kick start" evolution
by constructing primitive genetic codes and applying basic
selection and mutation operations. It is intended for use during the
early stages of development to save waiting around for chance discoveries.
"""

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.ggc_class_factory import GCABC, GGCDict
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG

# Initialize the Gene Pool Interface
gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)


# Load the primitive codons from the gene pool
PSQL_CDN_PRP_MSK = bytes.fromhex("723e9410d6590f0bb9b6bd51c4b2ef736ab0b7b2446def66744bd81f2845a98c")
PSQL_PRP_COLUMN = bytes.fromhex("0dad8776464ee2ea0441b9d3667db67b2d95223fa00b5db5a56008b4b92f3908")
PSQL_BITWISE_AND = bytes.fromhex("180b0075106e8118573c29de562a591d57ecda181ba75d445cef4b565e24694d")
PSQL_ORDERBY_RND = bytes.fromhex("0fa706b27f32c5faae00804337143eefe927f36efa24dd8d06e8499fcdedf5b4")
PSQL_WHERE = bytes.fromhex("c6da210e9930a4937b45b91e51a538e12976d0f0b08433638b2fcf1cbf560a7d")
GPI_SELECT_GC = bytes.fromhex("42d07451920d2bfcf3432909fe4460bcb4afb5a80771712a8a315b70a4c331c7")
SCA_GC = bytes.fromhex("dc734de92d199546c00249473954a81a3c0cc89fe85cc229d78e75f03f12a94d")


# Dictionary of primitive GCs
# This is empty on initialization and populated on first use
primitive_gcs: dict[str, GCABC] = {}


def cdn_prp_filter() -> GCABC:
    """Create the PSQL codon property filter genetic code.

    "properties" & MASK

    Returns:
        GCABC: The codon property filter genetic code.
    """
    return GGCDict()


def create_primitive_gcs():
    """Create the primitive genetic codes and store them in the primitive_gcs dict."""

    primitive_gcs["PSQL_CDN_PRP_MSK"] = gpi[PSQL_CDN_PRP_MSK]
    primitive_gcs["PSQL_PRP_COLUMN"] = gpi[PSQL_PRP_COLUMN]
    primitive_gcs["PSQL_BITWISE_AND"] = gpi[PSQL_BITWISE_AND]
    primitive_gcs["PSQL_ORDERBY_RND"] = gpi[PSQL_ORDERBY_RND]
    primitive_gcs["PSQL_WHERE"] = gpi[PSQL_WHERE]
    primitive_gcs["GPI_SELECT_GC"] = gpi[GPI_SELECT_GC]
    primitive_gcs["SCA_GC"] = gpi[SCA_GC]

    primitive_gcs["cdn_prp_filter"] = cdn_prp_filter()
