# Genetic Code Types

## Overview

A **Genetic Code Type** (GC Type) is a fundamental classification that determines the behavioral and structural characteristics of a genetic code within the Erasmus GP system. The GC Type defines:

- The **functional role** of the genetic code in evolved programs
- The **connection graph types** that can be used with the genetic code
- The **properties** that apply to the genetic code
- The **ancestral relationships** and creation mechanisms

The GC Type is stored as a 3-bit unsigned integer in the genetic code's [properties](properties.md) bitfield (bits 2:0) and is defined by the `GCType` enumeration in `egpcommon.properties`.

## The Three GC Types

### 1. Codon (GCType.CODON = 0)

**Codons** are the fundamental building blocks of evolved code—indivisible functional primitives that represent basic operations.

**Key Characteristics:**

- **Functional Primitives**: Represent a single operation or line of code (e.g., addition, comparison, function call)
- **Cannot Be Created at Runtime**: Codons are pre-defined and loaded from the genetic library; they are not evolved
- **No Ancestors**: Codons have no parent genetic codes (`gca`, `gcb`, `ancestora`, and `ancestorb` must be `None`). However, generated literal codons may have a physical genetic code (`pgc`) that created them.
- **Primitive Connection Graphs**: Must use `CGraphType.PRIMITIVE` connection graphs with no sub-GCs
- **Implicit Sub-GCs**: GCA and GCB are implicit (not present) in codon connection graphs
- **Language Implementation**: Can be implemented in Python (default) or PostgreSQL (via `gctsp` properties)

**Example Use Cases:**

- Arithmetic operations: `operator.add`, `operator.mul`
- Comparisons: `operator.eq`, `operator.lt`
- Type conversions: `int()`, `float()`
- Built-in functions: `len()`, `abs()`, `range()`

**Properties (gctsp when gc_type=0):**

- `literal` (bool): The codon output type is a literal (which requires special handling in some cases)
- `python` (bool): Codon code is Python (default: True)
- `psql` (bool): Codon code is PostgreSQL-flavored SQL

### 2. Ordinary (GCType.ORDINARY = 1)

**Ordinary** genetic codes represent the vast majority of evolved code—composite functions built from other genetic codes through evolution.

**Key Characteristics:**

- **Evolved Compositions**: Created at runtime through evolutionary processes by combining other genetic codes
- **Have Ancestors**: Possess parent genetic codes (`gca`, `gcb`) and ancestor references (`ancestora`, `ancestorb`)
- **Recursive Structure**: Built hierarchically from codons and other ordinary genetic codes
- **Standard Connection Graphs**: Typically use `CGraphType.STANDARD` but can also use conditional (`IF_THEN`, `IF_THEN_ELSE`) and loop (`FOR_LOOP`, `WHILE_LOOP`) graph types
- **Two Sub-GCs**: Contain exactly two sub-genetic codes (GCA and GCB) that are connected via their connection graph
- **Physical Creation**: Have a physical genetic code (`pgc`) that created them through evolutionary operations

**Evolutionary Properties:**

- Created by combining, mutating, or recombining existing genetic codes
- Subject to fitness evaluation and selection pressure
- Can be pulled from the genetic library or generated during runtime evolution
- Form the solution space that GP searches through

**Properties (gctsp when gc_type=1):**

- `simplification` (bool): The genetic code is eligible to be simplified by symbolic regression
- `python` (bool): Codon code is Python (default: True)
- `psql` (bool): Codon code is PostgreSQL-flavored SQL

## GC Type and Connection Graph Constraints

The GC Type constrains which connection graph types can be used:

| GC Type | Allowed CGraph Types |
| --------- | --------------------- |
| **CODON** | `PRIMITIVE` only |
| **ORDINARY** | `STANDARD`, `IF_THEN`, `IF_THEN_ELSE`, `FOR_LOOP`, `WHILE_LOOP`, `EMPTY` |

**Validation Rules:**

- If the connection graph is `PRIMITIVE` `gc_type` **must** be `CODON` and vice-versa.
- If the connection graph does not have a Row A defined, then `gca` **must** be NULL
- If the connection graph does not have a Row B defined, then `gcb` **must** be NULL
- If the connection graph has a Row A defined, then `gca` **must not** be NULL
- If the connection graph has a Row B defined, then `gcb` **must not** be NULL
- If the connection graph is `PRIMITIVE`: `ancestora` and `ancestorb` **must** be `None`

## Reserved Type

- **GCType.RESERVED_3 = 3**: Reserved for future use

## See Also

- [GC Properties](properties.md) - Complete properties bitfield specification
- [GC Logical Structure](gc_logical_structure.md) - Hierarchical structure of genetic codes
- [Connection Graphs](c_graph.md) - Connection graph types and rules
- [GC Relationships](gc_relationships.md) - Ancestral and network relationships
