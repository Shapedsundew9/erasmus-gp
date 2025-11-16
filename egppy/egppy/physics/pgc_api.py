"""PGC API module.

This module defines the canonical physical genetic-code (PGC) API types and
classes consumed by generated genetic code and by the EGP application. It is
the single source of truth for codon signatures, physical types and aliases,
ensuring that refactors or renames do not break codon signatures.

Responsibilities:
- Declare all public physical types and aliases consumed by generated code.
- Import any dependent EGP custom types so this module centralises type
    dependencies and avoids circular imports.
- Document verification expectations: application code invoked through this
    interface must perform aggressive verification and raise debug/fatal
    exceptions for API implementation or integration errors. Normal exceptions
    raised during execution of generated genetic code are expected and should be
    handled by the caller as part of normal operation.

Important:
- This module should remain stable in its exported types to preserve binary
    compatibility with generated code.
- The behaviour of critical helpers elsewhere (for example
    egpcommon.common.sha256_signature) must not be altered because other parts
    of the system depend on their exact semantics.
"""

# ALL types and EGP custom type dependencies MUST be imported here so
# that this module is the single source of truth, avoids circular imports
# and allows code refactoring/renaming without breaking codon signatures

# THIS IS A VERSIONED API MODULE

# pylint: disable=unused-import

from datetime import datetime
from numbers import Complex, Integral, Number, Rational, Real
from uuid import UUID

from egpcommon.common import NULL_UUID
from egpcommon.properties import PropertiesBD
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_constants import (
    CPI,
    DstIfKey,
    DstRow,
    EPClsPostfix,
    SrcIfKey,
    SrcRow,
)
from egppy.genetic_code.egc_class_factory import EGCDict as EGCode
from egppy.genetic_code.endpoint import DstEndPoint, EndPoint, SrcEndPoint
from egppy.genetic_code.ggc_class_factory import GGCDict as GGCode
from egppy.genetic_code.interface import DstInterface, Interface, SrcInterface
from egppy.genetic_code.types_def import TypesDef, types_def_store

# PGC operations
from egppy.physics.insertion import (
    harmony,
    insert_gc_case_0,
    insert_gc_case_1,
    inverse_stack,
    perfect_stack,
    sca,
    stack,
)

# PSQL Types - Import all types used in types.json
from egppy.physics.psql_types import (
    PsqlArray,
    PsqlBigInt,
    PsqlBigIntArray,
    PsqlBool,
    PsqlBoolArray,
    PsqlBytea,
    PsqlChar,
    PsqlDate,
    PsqlDoublePrecision,
    PsqlDoublePrecisionArray,
    PsqlFragment,
    PsqlFragmentOrderBy,
    PsqlFragmentWhere,
    PsqlInt,
    PsqlIntArray,
    PsqlIntegral,
    PsqlNumber,
    PsqlNumeric,
    PsqlReal,
    PsqlRealArray,
    PsqlSmallInt,
    PsqlSmallIntArray,
    PsqlTime,
    PsqlTimestamp,
    PsqlType,
    PsqlUUID,
    PsqlVarChar,
)
from egppy.physics.runtime_context import RuntimeContext

# Public Physical Types and Aliases
Pair = tuple
Triplet = tuple
Quadruplet = tuple
Quintuplet = tuple
Sextuplet = tuple
Septuplet = tuple
Bytes = bytes | bytearray


# The custom PGC function placeholder
def custom_pgc(_: RuntimeContext) -> None:
    """Custom PGC mutation function placeholder.

    This function is a no-op placeholder representing a custom mutation
    function implemented outside of the standard EGP system. It allows
    generated genetic code to include calls to custom mutation functions
    without knowing their implementation details.

    Args:
        _: The runtime context for the genetic code execution.

    Returns:
        None
    """
    pass
