# Language Operator Definition JSON Format Specification

## Overview

This format defines operators/functions for a language, mapping each symbol to a definition object. It supports code generation, documentation, and type validation.

## Schema Definition

| Key Name      | Data Type         | Required | Description                                                                                   |
|---------------|-------------------|----------|-----------------------------------------------------------------------------------------------|
| (operator)    | object            | Yes      | The operator/function symbol (e.g., "+", "find1", "<"). Each maps to a definition object.     |
| inline        | string            | Yes      | Template string for code generation, with placeholders `{i0}`, `{i1}`, etc.                   |
| description   | string            | Yes      | Human-readable description of the operator/function.                                          |
| inputs        | array of strings  | No*      | List of input types, in order. Mutually exclusive with `num_inputs`.                          |
| num_inputs    | integer           | No*      | Number of inputs. Mutually exclusive with `inputs`.                                           |
| outputs       | array of strings  | No**     | List of output types, in order. Mutually exclusive with `num_outputs`.                        |
| num_outputs   | integer           | No**     | Number of outputs. Mutually exclusive with `outputs`.                                         |
| properties    | object            | No       | Additional metadata. Keys/values defined in `egpcommon/properties.py`.                        |

\* If neither `inputs` nor `num_inputs` is specified, default: `inputs = [filename]*2` (filename = JSON file name, strip leading underscore).
** If neither `outputs` nor `num_outputs` is specified, default: `outputs = [filename]` (filename = JSON file name, strip leading underscore).

## Type String Rules

- Type strings are standardized across all files.
- If a type string starts with `-` and ends with a single digit (e.g., `-Number0`), all uses of that template (e.g., `-Number0`) must be the same actual type within an operator invocation.
- Different templates (e.g., `-Number0`, `-Number1`) may be different types, but all instances of a given template must match.

## Properties

- The `properties` object must use keys and values as defined in `egpcommon/properties.py`.
- Reference to `egpcommon/properties.py` is sufficient for documentation.

## Validation Rules

- `inputs` and `num_inputs` are mutually exclusive; only one may be present.
- If `num_inputs` is present, derive `inputs` as `[filename]*num_inputs`.
- If neither is present, default to `[filename]*2`.
- Same rules apply for `outputs` and `num_outputs`, with default of 1 output.
- Type templates (e.g., `-Type0`) must be used consistently within an operator definition.

## Full Example

```json
{
  "find1": {
    "inline": "{i0}.find({i1})",
    "description": "find",
    "inputs": ["str", "str"],
    "outputs": ["int"],
    "properties": {
      "python": true,
      "psql": false
    }
  },
  "<": {
    "inline": "pqsl_lt({i0}, {i1})",
    "description": "PSQL less than {t0} with {t1}",
    "num_inputs": 2,
    "outputs": ["PsqlBool"],
    "properties": {
      "python": false,
      "psql": true
    }
  }
}
```

## Ambiguities & Questions

- None outstanding; all rules for defaults, templates, and properties are now explicit.
