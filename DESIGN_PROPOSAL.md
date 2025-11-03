# Design Proposal: Separating Endpoints from Connections

## Problem Statement

The current design embeds connection references (`refs`) within `EndPoint` objects. This creates a deduplication problem:

- `EndPoint` objects are designed to be freezable and deduplicated for memory efficiency
- However, connections change frequently during graph construction
- Once an `EndPoint` is frozen, it cannot be modified (including its refs)
- This means we can't effectively deduplicate endpoints because each unique set of connections creates a distinct endpoint object
- Analysis shows `.refs` is accessed in ~86 locations across the codebase

## Root Cause Analysis

The fundamental issue is **conflation of identity and relationships**:

1. **Endpoint Identity**: `(row, idx, cls, typ)` - stable, rarely changes
2. **Endpoint Connections**: `refs` - dynamic, changes during graph construction
3. **Current Design**: Both are in the same object, preventing effective deduplication

Example problem scenario:
```python
# These should be the same deduplicated endpoint:
ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int", refs=[["I", 0]])
ep2 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int", refs=[["I", 1]])
# But they can't be deduplicated because refs differ!
```

## Proposed Solution

### Option 1: Connection Objects (Recommended)

Create a separate `Connection` class and move connection management to `Interface`:

#### 1.1 New Connection Class

```python
class Connection(FreezableObject):
    """Represents a connection between two endpoints in a connection graph.
    
    A connection links a source endpoint (row, idx) to a destination endpoint (row, idx).
    Connections are immutable once frozen and can be deduplicated.
    """
    __slots__ = ("src_row", "src_idx", "dst_row", "dst_idx", "_hash")
    
    def __init__(
        self,
        src_row: SrcRow,
        src_idx: int,
        dst_row: DstRow,
        dst_idx: int,
        frozen: bool = False
    ) -> None:
        super().__init__(False)
        self.src_row = src_row
        self.src_idx = src_idx
        self.dst_row = dst_row
        self.dst_idx = dst_idx
        self._hash: int = 0
        if frozen:
            self.freeze()
    
    def __hash__(self) -> int:
        if self.is_frozen():
            return self._hash
        return hash((self.src_row, self.src_idx, self.dst_row, self.dst_idx))
    
    def freeze(self, store: bool = True) -> Connection:
        if not self._frozen:
            retval = super().freeze(store)
            object.__setattr__(
                self, "_hash", 
                hash((self.src_row, self.src_idx, self.dst_row, self.dst_idx))
            )
            return retval
        return self
```

#### 1.2 Simplified EndPoint Class

```python
class EndPoint(FreezableObject):
    """Endpoint identity without connections.
    
    An endpoint represents a typed parameter position in an interface.
    Connections to/from this endpoint are managed separately by Interface.
    """
    __slots__ = ("row", "idx", "cls", "_typ", "_hash")
    
    def __init__(
        self,
        row: Row,
        idx: int,
        cls: EndPointClass,
        typ: TypesDef | int | str,
        frozen: bool = False,
    ) -> None:
        super().__init__(False)
        self.row = row
        self.idx = idx
        self.cls = cls
        self.typ = typ
        self._hash: int = 0
        if frozen:
            self.freeze()
    
    # Remove refs property, connect(), is_connected()
    # Simplify __eq__ and __hash__ (no refs comparison)
```

#### 1.3 Enhanced Interface Class

```python
class Interface(FreezableObject):
    """Interface with separate endpoint identities and connections."""
    
    __slots__ = ("endpoints", "_connections", "_hash")
    
    def __init__(
        self,
        endpoints: Sequence[EndPoint] | ...,
        connections: dict[int, list[Connection]] | None = None,
        row: Row | None = None,
    ) -> None:
        super().__init__(frozen=False)
        self.endpoints: list[EndPoint] | tuple[EndPoint, ...] = []
        # Maps endpoint index -> list of connections
        self._connections: dict[int, list[Connection]] | dict[int, tuple[Connection, ...]] = (
            connections if connections is not None else {}
        )
        # ... initialization logic ...
    
    def get_connections(self, ep_idx: int) -> list[Connection]:
        """Get all connections for an endpoint by its index."""
        return self._connections.get(ep_idx, [])
    
    def add_connection(self, ep_idx: int, connection: Connection) -> None:
        """Add a connection for an endpoint."""
        if self.is_frozen():
            raise RuntimeError("Cannot modify frozen Interface")
        if ep_idx not in self._connections:
            self._connections[ep_idx] = []
        self._connections[ep_idx].append(connection)
    
    def connect(self, src_idx: int, dst_row: DstRow, dst_idx: int) -> None:
        """Connect an endpoint in this interface to a destination endpoint."""
        if self.is_frozen():
            raise RuntimeError("Cannot modify frozen Interface")
        ep = self.endpoints[src_idx]
        if ep.cls != EndPointClass.SRC:
            raise ValueError("Can only connect from source endpoints")
        conn = Connection(ep.row, ep.idx, dst_row, dst_idx)
        self.add_connection(src_idx, conn)
    
    def is_connected(self, ep_idx: int) -> bool:
        """Check if an endpoint has any connections."""
        return ep_idx in self._connections and len(self._connections[ep_idx]) > 0
    
    def unconnected_eps(self) -> list[EndPoint]:
        """Return list of endpoints with no connections."""
        return [ep for i, ep in enumerate(self.endpoints) 
                if not self.is_connected(i)]
```

### Option 2: Keep Refs but Make EndPoint Non-Deduplicatable (Not Recommended)

Keep current design but accept that endpoints can't be deduplicated effectively. This doesn't solve the memory efficiency goal.

## Benefits of Option 1

1. **Better Deduplication**: `EndPoint` objects with same (row, idx, cls, typ) can be deduplicated regardless of connections
2. **Cleaner Separation**: Endpoint identity vs. graph topology are distinct concerns
3. **Flexible Connections**: Add/remove connections without creating new endpoint objects
4. **Memory Efficiency**: 
   - Reuse endpoint objects across different connection patterns
   - Connection objects can also be deduplicated
5. **Better Semantics**: Makes it clear that connections are properties of the graph, not the endpoint

## Migration Path

### Phase 1: Create New Classes
1. ✅ Create `Connection` class in new file `connection.py`
2. ✅ Add deduplicator for Connection objects
3. ✅ Update `EndPoint` to remove `refs` and related methods

### Phase 2: Update Interface
1. Add `_connections` dict to `Interface`
2. Add connection management methods
3. Update initialization to handle both old and new formats (backward compat)
4. Update `to_json()` and other serialization methods

### Phase 3: Update Consumers
1. Update `CGraph` class to use new connection API
2. Update `code_connection.py` executor code
3. Update `execution_context.py` 
4. Update all test files (~86 references to `.refs`)

### Phase 4: Cleanup
1. Remove backward compatibility code
2. Update documentation
3. Performance testing and validation

## Impact Assessment

**Breaking Changes:**
- `EndPoint.refs` property removed
- `EndPoint.connect()` method removed  
- `EndPoint.is_connected()` method removed
- Interface initialization signature changes
- ~86 `.refs` access locations need updates

**Files Impacted:**
- `egppy/genetic_code/end_point.py` - Major changes
- `egppy/genetic_code/interface.py` - Major changes  
- `egppy/genetic_code/c_graph.py` - Moderate changes
- `egppy/worker/executor/code_connection.py` - Minor changes
- `egppy/worker/executor/execution_context.py` - Minor changes
- All test files - Extensive updates

**Estimated Effort:**
- Core implementation: 6-8 hours
- Test updates: 8-12 hours
- Testing and validation: 4-6 hours
- Total: ~20-26 hours

**Risks:**
- High: Many test failures during transition
- Medium: Potential for subtle bugs in connection handling
- Low: Performance regression (expecting improvement)

## Backward Compatibility Strategy

During transition, support both APIs:

```python
class Interface:
    def __init__(self, endpoints, connections=None, row=None, legacy_refs=True):
        # If legacy_refs=True and endpoints have .refs, convert to connections
        if legacy_refs:
            connections = self._extract_connections_from_refs(endpoints)
        # ... rest of init ...
```

## Testing Strategy

1. **Unit Tests**: Update all existing tests to use new API
2. **Integration Tests**: Ensure CGraph functionality preserved
3. **Performance Tests**: Validate deduplication improvements
4. **Backward Compat Tests**: Ensure legacy data can be loaded

## Alternative Considered: Lazy Refs

Keep refs in EndPoint but make them lazy/external references. Rejected because:
- Still prevents endpoint deduplication
- Adds complexity without solving core problem
- Makes endpoint state more complex
