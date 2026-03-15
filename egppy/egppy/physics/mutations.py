"""Mutations Module"""

# pylint: disable=unused-import
# We want to have all mutation types available from this module as a one stop shop
# for mutation functions
from egppy.physics.mutations.create import create
from egppy.physics.mutations.crossover import crossover
from egppy.physics.mutations.insert import insert, InsertionCase
from egppy.physics.mutations.wrap import wrap, WrapCase
