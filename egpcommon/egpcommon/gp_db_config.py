"""Gene Pool Database Configuration
This module contains the configuration for the Gene Pool database table.

The GP schema is used in egppy & egpdbmgr.
"""

from typing import Any

# GP GC Fields with Postgres definitions. Value dicts must be compatible
# with a ColumnSchema
EGC_KVT: dict[str, dict[str, Any]] = {
    "cgraph": {"db_type": "BYTEA", "nullable": False, "egp_type": "CGraph"},
    "gca": {"db_type": "BYTEA", "nullable": True, "egp_type": "GCASig"},
    "gcb": {"db_type": "BYTEA", "nullable": True, "egp_type": "GCBSig"},
    "ancestora": {"db_type": "BYTEA", "nullable": True, "egp_type": "AncestorASig"},
    "ancestorb": {"db_type": "BYTEA", "nullable": True, "egp_type": "AncestorBSig"},
    "pgc": {"db_type": "BYTEA", "nullable": True, "egp_type": "PGCSig"},
    "created": {"db_type": "TIMESTAMP", "nullable": False, "egp_type": "Created"},
    "properties": {"db_type": "BIGINT", "nullable": False, "egp_type": "PropertiesInt"},
    "signature": {"db_type": "BYTEA", "nullable": False, "primary_key": True, "egp_type": "GCSig"},
}
GGC_KVT: dict[str, dict[str, Any]] = EGC_KVT | {
    "_e_count": {"db_type": "INT", "nullable": False, "egp_type": "ECountHL"},
    "_e_total": {"db_type": "FLOAT", "nullable": False, "egp_type": "ETotalHL"},
    "_evolvability": {"db_type": "FLOAT", "nullable": False, "egp_type": "EvolvabilityHL"},
    "_f_count": {"db_type": "INT", "nullable": False, "egp_type": "FCountHL"},
    "_f_total": {"db_type": "FLOAT", "nullable": False, "egp_type": "FTotalHL"},
    "_fitness": {"db_type": "FLOAT", "nullable": False, "egp_type": "FitnessHL"},
    "_lost_descendants": {"db_type": "BIGINT", "nullable": False, "egp_type": "LostDescendantsHL"},
    "_reference_count": {"db_type": "BIGINT", "nullable": False, "egp_type": "ReferenceCountHL"},
    "code": {},  # Not persisted in the database but needed for execution
    "code_depth": {"db_type": "INT", "nullable": False, "egp_type": "CodeDepth"},
    "creator": {"db_type": "UUID", "nullable": False, "egp_type": "Creator"},
    "descendants": {"db_type": "BIGINT", "nullable": False, "egp_type": "Descendants"},
    "e_count": {"db_type": "INT", "nullable": False, "egp_type": "ECountCL"},
    "e_total": {"db_type": "FLOAT", "nullable": False, "egp_type": "ETotalCL"},
    "evolvability": {"db_type": "FLOAT", "nullable": False, "egp_type": "EvolvabilityCL"},
    "f_count": {"db_type": "INT", "nullable": False, "egp_type": "FCountCL"},
    "f_total": {"db_type": "FLOAT", "nullable": False, "egp_type": "FTotalCL"},
    "fitness": {"db_type": "FLOAT", "nullable": False, "egp_type": "FitnessCL"},
    "generation": {"db_type": "BIGINT", "nullable": False, "egp_type": "Generation"},
    "imports": {},  # Not persisted in the database but needed for execution
    "inline": {},  # Not persisted in the database but needed for execution
    "input_types": {"db_type": "INT[]", "nullable": False, "egp_type": "ITypes"},
    "inputs": {"db_type": "BYTEA", "nullable": False, "egp_type": "IIndices"},
    "lost_descendants": {"db_type": "BIGINT", "nullable": False, "egp_type": "LostDescendantsCL"},
    "meta_data": {"db_type": "BYTEA", "nullable": True},
    "num_codes": {"db_type": "INT", "nullable": False, "egp_type": "NumCodes"},
    "num_codons": {"db_type": "INT", "nullable": False, "egp_type": "NumCodons"},
    "num_inputs": {"db_type": "SMALLINT", "nullable": False, "egp_type": "NumInputs"},
    "num_outputs": {"db_type": "SMALLINT", "nullable": False, "egp_type": "NumOutputs"},
    "output_types": {"db_type": "INT[]", "nullable": False, "egp_type": "OTypes"},
    "outputs": {"db_type": "BYTEA", "nullable": False, "egp_type": "OIndices"},
    "population_uid": {"db_type": "SMALLINT", "nullable": False, "egp_type": "PopulationUID"},
    "problem": {"db_type": "BYTEA", "nullable": True, "egp_type": "ProblemSig"},
    "problem_set": {"db_type": "BYTEA", "nullable": True, "egp_type": "ProblemSetSig"},
    "reference_count": {"db_type": "BIGINT", "nullable": False, "egp_type": "ReferenceCountCL"},
    "survivability": {"db_type": "FLOAT", "nullable": False, "egp_type": "Survivability"},
    "updated": {"db_type": "TIMESTAMP", "nullable": False, "egp_type": "Updated"},
}
