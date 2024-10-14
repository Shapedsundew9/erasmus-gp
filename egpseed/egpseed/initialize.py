"""Generate codons.

Overview
========
Operators e.g. +, -, ~ etc. but also including functions/methods, are defined in the language folder
along with supported types. All combinations of type & operator are executed, catching the
exceptions and identifying which operator-type combinations are valid and what the type of the
results are (characterisation). From this information gc_types.json & codons.json are generated.

Structure
=========
In the languages folder there is a folder for each language that codons will be generated for.
Currently this is only python.
There is also operator_format.json which is a python Cerberus Validator schema used to validate
and normalise the the operators defined by the language.

In each language folder there is an operators folder and 2 files:
    types.json: Defines the types supported. Key:Value pairs common with the operator format
                are used to define cast operators.
    exceptions.json: Defines which exceptions merit which action

In the operators folder there is one or more .json files defining the operators for the language.
Operators will be aggregated in a single dictionary so the operator_key mujst be unique across
files. The breakdown of operators across files is a user organisation choice.

Operator Assumptions
--------------------
In general the following assumptions are made about all operator JSON data files. Each
assumption may be overridden in the definition. Assumptions are defined in operator_format.json.
    * Operations take 2 inputs
    * Operations are deterministic
    * Operations return a single output that is not an input object
    * i0 is the sequence object operated on.
    * If num_outputs = 0 then i0 has been modified.

NOTE: Containers are not yet supported for python
    "tuple": {
        "default": "(True, 2, 2.0, complex(2.0,-2.0))"
    },
    "list": {
        "default": "[True, 2, 2.0, complex(2.0,-2.0)]"
    },
    "dict": {
        "default": "{True:True, 2:2, 2.0:2.0, complex(2.0,-2.0):complex(2.0,-2.0)}"
    }
"""
from copy import deepcopy
from datetime import UTC, datetime
from itertools import product
from json import dump, load
from logging import DEBUG, Logger, NullHandler, getLogger
from os import listdir
from os.path import dirname, join
from sys import modules
from typing import Any

from cerberus import Validator

# pylint: disable=unused-import
from egppy.gc_graph.ep_type import (  # , fully_qualified_name
    _EGP_REAL_TYPE_LIMIT, asstr)
from egppy.gc_types.ggc_class_factory import GGCDirtyDict, XGCType
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM

_logger: Logger = getLogger(__name__)
_logger.addHandler(NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(DEBUG)

_path: str = dirname(__file__)
_template_file: str = join(_path, "data/languages/template.json")
_logger.debug("template_file: %s", _template_file)
_codon_file: str = join(_path, "../../egppy/egppy/data/codons.json")
_ep_type_file: str = join(_path, "../../egppy/egppy/data/ep_types.json")


_GC_MCODON_TEMPLATE: dict[str, Any] = {
    "graph": {"A": [], "O": [["A", 0, "To Be Defined"]]},
    "gca": None,
    "gcb": None,
    "creator": "22c23596-df90-4b87-88a4-9409a0ea764f",
    "created": datetime.now(UTC).isoformat(),
    "problem": ACYBERGENESIS_PROBLEM,
    "properties": {},
    "meta_data": {"function": {"python3": {"0": {"inline": "To Be Defined"}}}},
}


def _set_language(language):
    """Set the language to process.

    Determines the relative paths to the language definition files.

    Args:
        language (string): Name of a language folder under data/languages.

    Returns:
        list(str): List of operator files with relative path.
        str: types.json file with relative path
        str: exceptions.json file with relative path
        list(str): List of mutation files with relative path.
    """
    operator_path: str = join(_path, "data/languages", language, "operators")
    operator_files: list[str] = [
        join(operator_path, filename) for filename in listdir(operator_path)
    ]
    _logger.debug("operator_path: %s", operator_path)
    _logger.debug("operator_files: %s", operator_files)
    mutation_path: str = join(_path, "data/languages", language, "mutations")
    mutation_files: list[str] = [
        join(mutation_path, filename) for filename in listdir(mutation_path)
    ]
    exceptions_file: str = join(_path, "data/languages", language, "exceptions.json")
    types_file: str = join(_path, "data/languages", language, "types.json")
    return operator_files, types_file, exceptions_file, mutation_files


def _load_operators(operator_files, validator) -> dict[str, dict[str, Any]]:
    """Load & normalise the operators.

    Args:
        operator_files (list(str)): List of JSON files with operator definitions
        validator (Validator): Cerberus operator format validator

    Returns:
        dict(dict): A dictionary of normalised operator definitions.
    """
    operators: dict[str, dict[str, Any]] = {}
    for operator_file in operator_files:
        with open(operator_file, "r", encoding="utf-8") as file_ptr:
            _operators: dict[str, dict[str, Any]] = load(file_ptr)
        for key, operator in _operators.get("operators", {}).items():
            if key in operators:
                _logger.error(
                    "Operator is not unique. Duplicate %s found in %s.",
                    key,
                    operator_file,
                )
                raise RuntimeError("Duplicate operator.")
            if validator.validate(operator):
                operators[key] = validator.normalized(operator)
                if "output_types" in operator:
                    # This is python specific
                    operators[key]["output_types"] = operator["output_types"]
                    # [
                    #    fully_qualified_name(eval(f"{ot}()"))  # pylint: disable=eval-used
                    #    for ot in operator["output_types"]
                    #]
            else:
                _logger.error("%s\n%s", str(operator), validator.errors)
                print("Operator validation failed. See logs for details.")
                raise RuntimeError("Invalid operator.")
    return operators


def _load_mutations(mutation_files, validator) -> dict[str, dict[str, Any]]:
    """Load & normalise the mutations.

    Args:
        mutation_files (list(str)): List of JSON files with mutation definitions
        validator (Validator): Cerberus mutation format validator

    Returns:
        dict(dict): A dictionary of normalised mutation definitions.
    """
    mutations: dict[str, dict[str, Any]] = {}
    for mutation_file in mutation_files:
        with open(mutation_file, "r", encoding="utf-8") as file_ptr:
            _mutations: dict[str, dict[str, Any]] = load(file_ptr)
        for key, mutation in _mutations.get("operators", {}).items():
            if key in mutations:
                _logger.error(
                    "Mutation is not unique. Duplicate %s found in %s.",
                    key,
                    mutation_file,
                )
                raise RuntimeError("Duplicate mutation.")
            if validator.validate(mutation):
                mutations[key] = validator.normalized(mutation)
                # This is python specific
                if "input_types" in mutation:
                    mutations[key]["input_types"] = mutation["input_types"]
                    # [
                    #    fully_qualified_name(eval(f"{mt}()"))  # pylint: disable=eval-used
                    #    for mt in mutation["input_types"]
                    # ]
                if (
                    "num_inputs" in mutation
                    and mutation["num_inputs"] > 1
                    and len(mutations[key]["input_types"]) == 1
                ):
                    mutations[key]["input_types"] *= mutation["num_inputs"]
            else:
                _logger.error("%s\n%s", str(mutation), validator.errors)
                print("Mutation validation failed. See logs for details.")
                raise RuntimeError("Invalid mutation operator.")
    return mutations


def _load_types(type_file, operators, validator):
    """Load types, create type conversion/cast operators & cross-reference mapping.

    The 'operators' dictionary is modified: Type cast operators are added.

    Args:
        type_file (str): JSON file with the type definitions.
        operators (dict(dict)): Dictionary of normalised operator definitions to be appended.
        validator (Validator): Cerberus operator format validator.

    Returns:
        list(str): The list of fully qualified defined type names.
        dict(dict): Bi-directional mapping of fully qualified type name to UID
    """
    with open(type_file, "r", encoding="utf8") as file_ptr:
        _types: dict[str, dict[str, Any]] = load(file_ptr)
    types: list[str] = []
    for key, typ in tuple(_types.items()):
        _logger.debug("Current type: %s %s", key, typ)
        # obj: Any | None = eval(f"{key}()") if key != "None" else None  # pylint: disable=eval-used
        # name: str = fully_qualified_name(obj)
        name = key
        _types[key]["fully_qualified_type"] = name

        # Type casts use operator defaults then explicitly override as needed.
        constructor: dict[str, str] = typ.get(
            "constructor", {"inline": f"{key}({{i0}})"}
        )
        operators[name] = validator.normalized(constructor)
        operators[name]["num_inputs"] = typ.get(
            "num_inputs", operators[name]["num_inputs"]
        )
        operators[name]["num_outputs"] = typ.get(
            "num_outputs", operators[name]["num_outputs"]
        )
        if "output_types" in typ:
            operators[name]["output_types"] = typ["output_types"]
            # [fully_qualified_name(eval(f"{typ['output_types'][0]}()"))  # pylint: disable=eval-used]

        # A default value of '(*)' where * is wildcard is an instanciation of the object.
        # All objects are
        # imported as the fully qualified name and so this is appended.
        default: str | None = typ["default"]
        if (
            default is not None
            and len(default) > 1
            and default[0] == "("
            and default[-1] == ")"
        ):
            typ["default"] = name + default
        operators[name]["default"] = typ["default"]

        # Only real types in the type list as it is used with the operators.
        # Physical types construction operator gets the physical property set.
        if typ["uid"] >= _EGP_REAL_TYPE_LIMIT:
            types.append(name)
        else:
            operators[name]["properties"]["physical"] = True
    return types, _index_types(_types)


def _load(language):
    """Load the language definition.

    Operator definitions are loaded and normalised.
    Type names are expanded to the fully qualified name.

    Args:
        language (string): Name of a language folder under data/languages.

    Returns:
        dict(dict): Dictionary of operator definitions.
        dict(dict): Dictionary of type definitions.
        dict(list(str)): Exception identifiers for info, warning & error levels.
        dict(dict): Bi-directional mapping of fully qualified type name to UID
        dict(dict): Dictionary of mutuation definitions.
    """
    print(f"Loading language: {language}")
    (operator_files, type_file, exceptions_file, mutation_files) = _set_language(
        language
    )
    with open(
        join(_path, "data/languages/operator_format.json"), "r", encoding="utf-8"
    ) as file_ptr:
        validator = Validator(load(file_ptr), purge_unknown=True)  # type: ignore

    operators = _load_operators(operator_files, validator)
    types, indexed_types = _load_types(type_file, operators, validator)

    with open(
        join(_path, "data/languages/mutation_format.json"), "r", encoding="utf-8"
    ) as file_ptr:
        validator = Validator(load(file_ptr), purge_unknown=True)  # type: ignore
    mutations = _load_mutations(mutation_files, validator)

    with open(exceptions_file, "r", encoding="utf-8") as file_ptr:
        exceptions = load(file_ptr)

    return operators, types, exceptions, indexed_types, mutations


def _create_mcodon(operator, type_dict):
    """Create an mCodon definition from a normalised & characterised operator definition.

    Args:
        operator(dict): Normalised and characterised operator definition.
        type_dict(dict(dict)): See _index_types().

    Returns:
        codon(dict): An mCodon definition
    """
    codon = deepcopy(_GC_MCODON_TEMPLATE)
    codon["properties"] = operator["properties"]
    codon["evolvability"] = 1.0
    codon["e_count"] = 1
    codon["e_total"] = 1
    codon["fitness"] = 1.0
    codon["f_count"] = 1
    codon["f_total"] = 1
    for position, inpt in enumerate(operator["input_types"]):
        codon["graph"]["A"].append(["I", position, type_dict["n2v"][inpt]])
    if "imports" in operator:
        codon["meta_data"]["function"]["python3"]["0"]["imports"] = operator["imports"]
    codon["meta_data"]["function"]["python3"]["0"]["inline"] = operator["inline"]
    codon["meta_data"]["name"] = \
        f'{operator["name"]}({", ".join(operator["input_types"])})'
    for position, typ in enumerate(operator["output_types"]):
        codon["graph"]["O"][position][2] = type_dict["n2v"][typ]
    return codon


def _index_types(types):
    """Create a bi-directional mapping of type name <-> UID."""
    type_dict = {
        "n2v": {v["fully_qualified_type"]: v["uid"] for v in types.values()},
        "v2n": {v["uid"]: v["fully_qualified_type"] for v in types.values()},
        "instanciation": {
            v["uid"]: [
                v["instanciation"]["package"],
                v["instanciation"]["version"],
                v["instanciation"]["module"],
                k,
                v["instanciation"]["param"],
                v["default"],
            ]
            for k, v in types.items()
        },
    }

    # For convenience map all built in unqualified names to the UIDs of the fully qualified names
    type_dict["n2v"].update(
        {
            k.replace("builtins_", ""): v
            for k, v in type_dict["n2v"].items()
            if "builtins_" in k
        }
    )
    # type_dict["n2v"]["None"] = type_dict["n2v"]["NoneType"]
    # del type_dict["n2v"]["NoneType"]

    with open(_ep_type_file, "w", encoding="utf-8") as file_ptr:
        dump(type_dict, file_ptr, indent=4, sort_keys=True)
    return type_dict


def _generate(language):
    """Generate codon.json & gc_types.json for the specified language.

    Operators are iterated through, normalised & characterised for all combinations
    of types. Valid operators are converted to mCodons and saved in a JSON file.

    Args:
        language (string): Name of a language folder under data/languages.
    """
    operators, types, exceptions, type_dict, mutations = _load(language)
    # Only python supported at this stage.
    generator = python_generator
    codon_list = []

    # Operators
    tried = 0
    generated = 0
    for key, operator in tuple(operators.items()):
        for input_types in product(types, repeat=operator["num_inputs"]):
            result = generator(key, operators, input_types, exceptions)
            tried += 1
            if not operators[key]["num_outputs"] and not (
                operator["properties"]["object_modify"]
                or operator["properties"]["memory_modify"]
            ):
                _logger.fatal(
                    "Incomplete operator. Operator must modify state in some way. %s",
                    operators[key],
                )
                raise RuntimeError("Incomplete operator.")
            if result is not None:
                generated += 1
                result.setdefault("name", key)
                codon = _create_mcodon(result, type_dict)
                codon_list.append(GGCDirtyDict(codon).to_json())
    print(f"Generated {generated} codons from {tried} operator-type combinations"
          f" {generated * 100 / tried:0.1f}).")

    # Mutations
    for key, mutation in mutations.items():
        mutation.setdefault("name", key)
        codon = _create_mcodon(mutation, type_dict)
        codon_list.append(GGCDirtyDict(codon).to_json())
    print(f"Generated {len(mutations)} mutation codons.")

    with open(_codon_file, "w", encoding="utf-8") as file_ptr:
        dump(codon_list, file_ptr, indent=4, sort_keys=True)


def python_generator(key, operators, input_types, exceptions):
    """Characterise a specific normalised operator with a list of input types.

    Args:
        key(str): The operator key in the operators dictionary.
        operators(dict(dict)): Dictionary of normalised operators.
        input_types(list(str)): List of fully qualified input types to operator. The list is the
            same length as the operator has inputs.
        exceptions(dict(list(str))): Exception definitions for python. exceptions has the 
        following structure:
                "ok": [sub-strings]
                "info": [sub-strings]
                "warning": [sub-strings]
                "error": [sub-strings]
            sub-strings are partial exception strings but sufficient to be unique. If a sub-string
            matches an execption raised by characterising the operator the 'exceptions' key 
            defines what happens:
                "ok": This exception is raised but the operator-input_types is actually valid.
                "info": The exception means this operator-input_types combination is invalid.
                "warning": The exception is ambiguous the operator-input_types combination could be 
                           valid or invalid.
                "error": Something is wrong with the operator definition (needs fixing).
    """
    operator = deepcopy(operators[key])
    inputs = {"i" + str(n): operators[t]["default"] for n, t in enumerate(input_types)}
    for imp in (x for x in operator.get("imports", tuple()) if x["module"]):
        imp["name"] = (
            imp["module"].replace(".", "_") + "_" + imp["object"].replace(".", "_")
        )
        if imp["name"] not in dir(modules[python_generator.__module__]):
            exec(f"from {imp['module']} import {imp['object']} as {imp['name']}", globals())  # pylint: disable=exec-used
    expression = f"{operator['inline']}".format_map(inputs)
    operator["input_types"] = input_types
    try:
        result = eval(expression)  # pylint: disable=eval-used
    except Exception as excptn:  # pylint: disable=broad-exception-caught
        exception = str(excptn)
        for level in ("info", "warning", "error"):
            for etext in exceptions[level]:
                if etext in exception:
                    getattr(_logger, level)("Expression: %s, Exception: %s", expression, exception)
                    return None
            for etext in exceptions["ok"]:
                if etext in exception:
                    if not operator["num_outputs"] and not (
                        operator["properties"]["object_modify"]
                        or operator["properties"]["memory_modify"]
                    ):
                        _logger.fatal(
                            "No output_type or global state modification for operator %s",
                            operator
                        )
                        raise RuntimeError("Incomplete operator.") from excptn
                    else:
                        operator.setdefault("output_types", [])
                        return operator
            _logger.fatal(
                "Expression: %s, generated unrecognised exception: '%s' using operator: %s",
                expression,
                exception,
                operator,
            )
        raise RuntimeError("Unrecognised exception.") from excptn
    # FIXME: Hack for now. Need to fix unique import name and fully qualified name.
    rtype = result.__class__.__qualname__
    none_str = None.__class__.__qualname__
    typ = "None" if rtype == none_str else rtype
    operator["output_types"] = [typ]  # [fully_qualified_name(result)]
    return operator
