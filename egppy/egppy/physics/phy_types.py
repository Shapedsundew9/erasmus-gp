"""Maps EGP GC fields to EGP types that can be extracted and manipulated
by physical GC's. The typing structure is designed to map to the field use
cases and reduce the search space for valid and useful physical GC's."""

# TODO: Presently types are restricted to DB searchable fields. These need to
# be expanded to include all relevant fields for physical GC's manipluation
# e.g. CGraph, Interface, EndPoint etc.

# ALL types and EGP custom type dependencies MUST be imported here so
# that this module is the single source of truth, avoids circular imports
# and allows code refactoring/renaming without breaking codon signatures
from datetime import datetime

# This module is the sole module for type definitions for physical types
# allowing EGP code to be refactored and renamed without impacting codon signatures.
# As a result some imported objects & types are not used locally.
# pylint: disable=unused-import
from egpcommon.properties import PropertiesBD
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.types_def import TypesDef, types_def_store

# Some types are sub-classed as they represent fundamental types that have
# properties that could be validated rather than just use cases.


# A signature is a bytes object but a bytes object is not a Signature
class Signature(bytes):
    "A base class for all signature types"

    pass


# There are multiple types of signatures that do not overlap
class GCSig(Signature):
    "A signature for GC"

    pass


class ProblemSig(Signature):
    "A signature for Problem"

    pass


class ProblemSetSig(Signature):
    "A signature for Problem Set"

    pass


# The various ways a GC signature can be used
# Since they are interchangable they are aliases
# The existence of these aliases allows for more readable code
# and a bias toward using them for the role they have but not
# restricting them to it.
AncestorSig = GCSig
GCABSig = GCSig
PGCSig = GCSig

# Ancestor signatures
AncestorASig = AncestorSig
AncestorBSig = AncestorSig

# GCA & GCB
GCASig = GCABSig
GCBSig = GCABSig


# Properties are integers when pulled from the GP
class PropertiesInt(int):
    "A class for properties represented as integers"

    pass


# Created and Updated are datetime objects
class Created(datetime):
    "A class for created timestamps"

    pass


class Updated(datetime):
    "A class for updated timestamps"

    pass


# Interfaces & types
class IOTypes(tuple[TypesDef, ...]):
    "A class for input/output types (tuple of TypesDef)"

    pass


class IOIndices(bytes):
    "A class for input/output indices (bytes)"

    pass


ITypes = IOTypes
IIndices = IOIndices
OTypes = IOTypes
OIndices = IOIndices

# Dynamic, context independent, metrics have a higher layer, HL, and a current layer, CL type
ECount = int
ECountHL = ECount
ECountCL = ECount
ETotal = float
ETotalHL = ETotal
ETotalCL = ETotal
Evolvability = float
EvolvabilityHL = Evolvability
EvolvabilityCL = Evolvability
FCount = int
FCountHL = FCount
FCountCL = FCount
FTotal = float
FTotalHL = FTotal
FTotalCL = FTotal
Fitness = float
FitnessHL = Fitness
FitnessCL = Fitness
LostDescendants = int
LostDescendantsHL = LostDescendants
LostDescendantsCL = LostDescendants
ReferenceCount = int
ReferenceCountHL = ReferenceCount
ReferenceCountCL = ReferenceCount

# Static metrics
CodeDepth = int
Descendants = int
Generation = int
NumCodes = int
NumCodons = int
NumInputs = int
NumOutputs = int

# Dynamic, context dependent, metrics
Survivability = float


# Other
class PopulationUID(int):
    "A class for population unique identifiers"

    pass
