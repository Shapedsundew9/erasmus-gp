"""Mutations Module"""

from egppy.genetic_code.egc_dict import EGCDict
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_dict import GGCDict

# pylint: disable=unused-import
# We want to have all mutation types available from this module as a one stop shop
# for mutation functions
from egppy.physics.insert import insert
from egppy.physics.wrap import wrap


# Create
# The Create mutation is a specific kind of Wrap mutation. It is called out as its own type due to
# the importance of its use case. The Create mutation process takes an Empty Genetic Code CGraph
# definition
# and fills it with a GCA and GCB sub-genetic codes to make a standard CGraph. The choice of GCA &
# GCB
# is left to the selectors. For the Create mutation implementation it is all about how the genetic
# code
# is structured.
def create(empty: EGCDict, gca: GCABC, gcb: GCABC) -> EGCDict:
    """Create a standard CGraph ordinary GC by inserting gca & gcb into empty.

    Required connectivity for a create() mutation is that a primary connection between
      Is & Ad
      As & Bd
      Bs & Od
    exist. All other connectivity only need abide by the standard CGraph connectivity rule.
    NOTE: empty is not modified it is copied, modified and returned.

    Args
      empty: An EMPTY CGraph genetic code.
      gca: EGCDict or GCCode to be set as GCA
      gcb: EGCDict or GCCode to be set as GCB

    Returns
      EGCDict: The (likely unstable) new standard CGraph GC.
    """
    # TODO: Create a new_egc()) from empty
    # TODO: Set GCA & GCB to gca and gcb respectively
    # TODO: Add the row A & row interfaces
    # TODO: Establish the required connections
    # return new unstabilized standard CGraph GC


# Wrap
# The wrapping mutation has multiple sub-types that define all the ways the genetic codes,
# GCA & GCB, can be stuck together without a 3rd defining the interface (which would be the
# create or empty GC use case). The sub-types have their own connectivity requirements and
# are implemented in a dedicated wrap.py module. The import into this module is simply to
# provide a one stop shop for all primitive mutation functions.


# Insert
# Like wrap insert has multiple sub-type that are defined in a seperate insert.py module.
# The import here is for convinience.


# Crossover
# Cross over mutations try to preserve the connectivity of the parent genetic codes. The idea
# being that minimizing changes reduces staility risk.
