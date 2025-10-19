"""This module contains functions for querying the gene pool data.
It assumes that the gene pool is a database and that the data is stored
in a specific format. It also makes use of PostgreSQLisms for querying.
"""

from typing import LiteralString

from egpcommon.egp_log import DEBUG, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Steady state exception filters.
_LMT: LiteralString = " NOT ({exclude_column} = ANY({exclusions})) ORDER BY RANDOM() LIMIT 1"
_IT: LiteralString = "{input_types}"
_OT: LiteralString = "{output_types}"
_ITS: LiteralString = "{itypes}::INT[]"
_OTS: LiteralString = "{otypes}::INT[]"
_IDX: LiteralString = "{inputs} = {iidx}"
_ODX: LiteralString = "{outputs} = {oidx}"


# Match functions
def wrapper(t: str) -> str:
    """Wrap the SQL query with column exclusions and a limit"""
    return "WHERE " + t + " AND " + _LMT


def types_match(t: str, ts: str) -> str:
    """Match types exactly using the PostgreSQL array operator."""
    return t + " = " + ts


def exact_match(t: str, ts: str, dx: str) -> str:
    """Match types and positions exactly using the PostgreSQL array operator and exact match."""
    return types_match(t, ts) + " AND " + dx


def subset_match(t: str, ts: str) -> str:
    """Match types as a subset using the PostgreSQL array operator."""
    return t + " <@ " + ts


def overlap_match(t: str, ts: str) -> str:
    """Match types as an overlap using the PostgreSQL array operator."""
    return t + " && " + ts


def superset_match(t: str, ts: str) -> str:
    """Match types as a superset using the PostgreSQL array operator."""
    return t + " @> " + ts


# Match types
# Key coding is thus:
#   IxOx
# where
#   I = Input
#   O = Output
#   x = E, T, S, B, O or A
# and
#   E = Exact
#   T = Type
#   S = Superset
#   B = Subset
#   O = Overlap
#   A = Any
IF_MATCH_TYPES: dict[str, str] = {
    "IEOE": wrapper(exact_match(_IT, _ITS, _IDX) + " AND " + exact_match(_OT, _OTS, _ODX)),
    "ITOE": wrapper(types_match(_IT, _ITS) + " AND " + exact_match(_OT, _OTS, _ODX)),
    "IBOE": wrapper(subset_match(_IT, _ITS) + " AND " + exact_match(_OT, _OTS, _ODX)),
    "ISOE": wrapper(superset_match(_IT, _ITS) + " AND " + exact_match(_OT, _OTS, _ODX)),
    "IOOE": wrapper(overlap_match(_IT, _ITS) + " AND " + exact_match(_OT, _OTS, _ODX)),
    "IAOE": wrapper(exact_match(_OT, _OTS, _ODX)),
    "IEOT": wrapper(exact_match(_IT, _ITS, _IDX) + " AND " + types_match(_OT, _OTS)),
    "ITOT": wrapper(types_match(_IT, _ITS) + " AND " + types_match(_OT, _OTS)),
    "IBOT": wrapper(subset_match(_IT, _ITS) + " AND " + types_match(_OT, _OTS)),
    "ISOT": wrapper(superset_match(_IT, _ITS) + " AND " + types_match(_OT, _OTS)),
    "IOOT": wrapper(overlap_match(_IT, _ITS) + " AND " + types_match(_OT, _OTS)),
    "IAOT": wrapper(types_match(_OT, _OTS)),
    "IEOB": wrapper(exact_match(_IT, _ITS, _IDX) + " AND " + subset_match(_OT, _OTS)),
    "ITOB": wrapper(types_match(_IT, _ITS) + " AND " + subset_match(_OT, _OTS)),
    "IBOB": wrapper(subset_match(_IT, _ITS) + " AND " + subset_match(_OT, _OTS)),
    "ISOB": wrapper(superset_match(_IT, _ITS) + " AND " + subset_match(_OT, _OTS)),
    "IOOB": wrapper(overlap_match(_IT, _ITS) + " AND " + subset_match(_OT, _OTS)),
    "IAOB": wrapper(subset_match(_OT, _OTS)),
    "IEOS": wrapper(exact_match(_IT, _ITS, _IDX) + " AND " + superset_match(_OT, _OTS)),
    "ITOS": wrapper(types_match(_IT, _ITS) + " AND " + superset_match(_OT, _OTS)),
    "IBOS": wrapper(subset_match(_IT, _ITS) + " AND " + superset_match(_OT, _OTS)),
    "ISOS": wrapper(superset_match(_IT, _ITS) + " AND " + superset_match(_OT, _OTS)),
    "IOOS": wrapper(overlap_match(_IT, _ITS) + " AND " + superset_match(_OT, _OTS)),
    "IAOS": wrapper(superset_match(_OT, _OTS)),
    "IEOO": wrapper(exact_match(_IT, _ITS, _IDX) + " AND " + overlap_match(_OT, _OTS)),
    "ITOO": wrapper(types_match(_IT, _ITS) + " AND " + overlap_match(_OT, _OTS)),
    "IBOO": wrapper(subset_match(_IT, _ITS) + " AND " + overlap_match(_OT, _OTS)),
    "ISOO": wrapper(superset_match(_IT, _ITS) + " AND " + overlap_match(_OT, _OTS)),
    "IOOO": wrapper(overlap_match(_IT, _ITS) + " AND " + overlap_match(_OT, _OTS)),
    "IAOO": wrapper(overlap_match(_OT, _OTS)),
    "IEOA": wrapper(exact_match(_IT, _ITS, _IDX)),
    "ITOA": wrapper(types_match(_IT, _ITS)),
    "IBOA": wrapper(subset_match(_IT, _ITS)),
    "ISOA": wrapper(superset_match(_IT, _ITS)),
    "IOOA": wrapper(overlap_match(_IT, _ITS)),
    "IAOA": "WHERE " + _LMT,
}


if _logger.isEnabledFor(DEBUG):
    for key, match_type in IF_MATCH_TYPES.items():
        _logger.log(DEBUG, "Match type %s SQL: %s", key, match_type)


if __name__ == "__main__":
    # Test the match types
    for key, match_type in IF_MATCH_TYPES.items():
        print(f"Match type {key}: f'{match_type}'")
        print(f"Match type {key}: f'{match_type}'")
