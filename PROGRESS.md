# Erasmus GP - Development Progress Log

## [2026-03-01]

### Session Initialization

- Created `PROGRESS.md` to track chat history and project decisions.
- Current editor context: `/workspaces/erasmus-gp/docs/components/core/genetic_code/gc_types.md`.

### Documentation & Alignment: Genetic Code & Connection Graphs

- **Identified Discrepancies**: Investigated inconsistencies between docs (`docs/components/core/genetic_code/`) and the implementation (`egppy/egppy/genetic_code/`, `egpcommon/egpcommon/properties.py`).
- **Resolved Bitfield & Property Mismatches**: 
  - Updated `properties.py` to remove the defunct `template` property for Codons and expand the `reserved6` bit range.
  - Re-generated and updated `docs/components/core/genetic_code/properties.md` to accurately reflect the 3-bit `gc_type` and 4-bit `graph_type` bitfield offsets and sizes.
- **Resolved GC Types Documentation**: 
  - Updated `gc_types.md` to note the correct bit lengths.
  - Swapped `literal` and `simplification` gctsp properties between CODON (0) and ORDINARY (1) to align with actual Python implementations.
  - Clarified Codon ancestry: Updated rule to state that `gca`, `gcb`, `ancestora`, and `ancestorb` must be `None`, but `pgc` *can* exist for generated literal codons.
  - Updated primitive connection graph validation to note that `pgc` is not forced to be None.
- **JSON CGraph Format Clarification**:
  - Investigated the JSON CGraph format structure (specifically dealing with `[]` empty arrays for non-existent connections).
  - Validated that `[]` is permitted (except for the `U` row) and is strictly used to inform the system of the `graph_type` when no explicit connections exist (e.g., `{"A": [], "O": []}` = PRIMITIVE).
  - Confirmed via `test_infer.py` that signature generation is completely deterministic and ambiguity-free because `json_cgraph_to_interfaces()` infers missing empty interfaces during parsing, and `FrozenCGraph.to_json(True)` always normalizes the dictionary back out to explicit empty arrays before passing to the signature generator.
  - Updated `graph.md` to fully document the JSON structure, rules for `[]`, and the signature normalization process.


- **New Overview Documentation**:
  - Created `docs/components/core/genetic_code/overview.md` to provide a high-level conceptual explanation of what a Genetic Code is and how it solves evolutionary computation problems.
  - Included an architectural mermaid diagram showing the relationships between Core Dicts, Connection Graphs, Interfaces, and the Type System.
  - Documented the practical use-cases of the various components in the `egppy.genetic_code` package (e.g. `CGraph` vs `FrozenCGraph`, `GGCDict` vs `EGCDict`).


### Mermaid Chart & Architectural Alignment
- **Overview Alignment**:
  - Updated the architectural Mermaid chart in `docs/components/core/genetic_code/overview.md` to correctly use the desaturated semantic colors defined in the `style_guide.md` (e.g. dataBlue for Core representations, dataPlum for Graphs).
  - Clarified `EGCDict` as **Embryonic Genetic Code** (mutable, active evolution subset) and `GGCDict` as the full immutable dictionary containing cryptographic signatures.
  - Detailed the 'Frozen Optimization': clarified that unlike a mutable `Interface` (which holds a list of `Endpoint` objects), a `FrozenInterface` does **not** store `FrozenEndpoint` objects. Instead, it stores highly deduplicated tuples of type data and references, and generates `FrozenEndpoint` objects virtually (on-the-fly) when accessed, drastically reducing memory overhead.


### CGraph Documentation Alignment
- **File Renaming**: Renamed `docs/components/core/genetic_code/graph.md` to `c_graph.md` to match the internal naming conventions and updated all internal links (`definitions.md` and `gc_types.md`).


  - Fixed Primitive graph exclusion from row U connections in the Connectivity Requirements Legend.


### TypesDefStore Investigation
- **Type Database Architecture**:
  - Investigated `TypesDefStore` (`egppy/egppy/genetic_code/types_def_store.py`), a double-dictionary memory cache sitting on top of a local PostgreSQL database that stores type information (`types_def` table).
  - The cache evicts based on LRU policies (`_ancestors_cache`, `_descendants_cache`).
- **Dynamic Type Generation**:
  - Traced how new compound types (like `dict[str, float]`) are generated dynamically at runtime if they do not exist in the database.
  - The system dynamically resolves base templates and recursively constructs parents (e.g. creating `MutableMapping[str, float]` and `Mapping[str, float]` on the fly before creating the dictionary type), then pushes the new types into the PostgreSQL database.
- **Type Co/Contravariance Constraint**:
  - Discovered a significant limitation in the Type System inheritance graph: generic types currently do not support covariance. For example, while `int` is a subclass of `Number`, `dict[str, int]` is **not** recognized as a subclass of `dict[str, Number]`.
  - The `ancestors()` query for `dict[str, int]` yields `Mapping[str, int]` and `object`, but entirely misses `dict[str, Number]`.
  - **Impact on CGraph:** Because `CGraph.connect_all()` relies strictly on `dep.typ in types_def_store.ancestors(sep.typ)`, the connection logic is invariant. A destination requiring `list[Number]` will mathematically reject a source providing `list[int]`.


- **Bug Discovery (Type Covariance)**:
  - Created a bug report (`docs/components/core/genetic_code/covariance_bug.md`) detailing a failure in the Type System to recognize covariance in dynamically generated templates (e.g. `dict[str, int]` is incorrectly evaluated as incompatible with `dict[str, Number]`).
  - Outlined a recommended fix to compute covariance at connection time instead of inflating the database with combinatorial permutation rows.


  - Implemented `is_compatible()` within `TypesDefStore` to resolve the covariant type limitations dynamically at connection validation time.
  - Refactored `CGraph.connect_all()`, `FrozenCGraph._verify_type_consistency()`, and `FrozenEndPoint` connectivity checks to utilize `is_compatible()` instead of direct `ancestors()` intersection, unlocking robust type-safe polymorphic sub-GC connections during mutations.


- **Type System Documentation**:
  - Wrote a comprehensive guide in `docs/components/core/genetic_code/types/types_system.md` explaining the architecture of the Type System.
  - Formatted Mermaid graphs adhering strictly to the `style_guide.md` conventions, illustrating the relationship between the Cache, Database, and Dynamic Type Generator.
  - Documented the new `is_compatible` Generic Duck-Typing algorithm that facilitates Covariance.


### Cache Bug Fix
- Fixed a silent bug in `TypesDefStore.amend_children`. When dynamically generating types and linking them back as children to their parents, the code was invalidating the *ancestors* cache of the parent instead of the *descendants* cache of the parent's ancestors.


- **Added Unit Tests**:
  - Implemented `test_is_compatible_inheritance` and `test_is_compatible_covariance` to strictly ensure covariance functions correctly during mutations.
  - Implemented `test_descendants_cache_invalidation_on_new_type` to ensure that adding new compound children forces invalidations up the ancestor chain properly.

## [2026-03-15]

### Bootstrap Mutations Implementation (003-bootstrap-mutations)

- **Implemented Mutation Primitives**:
  - Implemented all 10 planned mutation primitives: `Rewire`, `Delete`, `Split`, `Iterate`, `Create`, `Wrap`, `Insertion`, `Crossover`, `DCE`, and `Unused Parameter Removal` (stub).
  - Ensured **Transactional Atomicity (FR-010)**: All mutations now use `copy_rgc()` to work on deep copies, returning a new `EGCode` object and leaving the original unchanged.
  - Implemented **Interface Compatibility (FR-011)**: All structural mutations now verify type compatibility using `can_connect()` or `can_downcast_connect()`.
  - Enforced **Maximum Graph Size (FR-008)**: Added `verify_graph_size()` in `mutations/common.py` and integrated it into all mutation primitives.

- **Refined Connection Processes**:
  - Implemented logic for `Create`, `Wrap`, `Insertion`, and `Crossover` connection processes in `egppy/egppy/physics/processes.py`.
  - Enhanced `force_primary()` with an `overwrite` parameter to support mandatory re-routing during `Insertion`.
  - Added `crossover_connection_process` with interface update and connection preservation logic.

- **Dead Code Elimination (FR-007)**:
  - Implemented reachability analysis algorithm in `egppy/egppy/physics/optimization.py`.
  - Created `dce` mutation primitive that removes unreachable sub-GCs and their corresponding interfaces.

- **Infrastructure & Bug Fixes**:
  - Fixed **Unhashable Interface Bug**: Modified `FrozenCGraph.consistency()` to skip hash recomputation for mutable `CGraph` instances, resolving a `TypeError` introduced by WP5.
  - Fixed **PropertiesBD Initialization Bug**: Updated `merge_properties()` in `helpers.py` to correctly handle `BitDict` objects and avoid redundant/invalid initializations.
  - Fixed **EGCDict Member Preservation**: Updated `copy_rgc()` to explicitly preserve extra members like `num_codes` which were being lost during `EGCDict` re-initialization.

- **Verification**:
  - Created a comprehensive unit test suite in `tests/test_egppy/test_physics/test_mutations.py` covering all mutation primitives and edge cases.
  - Verified that all 10 tests pass, confirming behavioral correctness and structural integrity.


