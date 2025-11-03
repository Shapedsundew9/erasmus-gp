# Endpoint-Connection Architecture Refactoring

## Current Architecture (Before)

```mermaid
graph TD
    subgraph "Current Design"
        EP1[EndPoint<br/>row: A, idx: 0<br/>typ: int<br/>refs: I, 0]
        EP2[EndPoint<br/>row: A, idx: 0<br/>typ: int<br/>refs: I, 1]
        EP3[EndPoint<br/>row: A, idx: 0<br/>typ: int<br/>refs: I, 0]
    end
    
    Problem1[❌ EP1 and EP3 have same identity<br/>but different refs prevent deduplication]
    Problem2[❌ Refs are part of endpoint<br/>freezing endpoint freezes connections]
    Problem3[❌ Can't change connections<br/>without creating new endpoint]
    
    EP1 -.-> Problem1
    EP3 -.-> Problem1
    EP1 --> Problem2
    EP2 --> Problem3
```

## Proposed Architecture (After)

```mermaid
graph TD
    subgraph "Endpoint Layer - Pure Identity"
        EP[EndPoint<br/>row: A, idx: 0<br/>typ: int]
        style EP fill:#90EE90
    end
    
    subgraph "Connection Layer - Relationships"
        C1[Connection<br/>src: I,0 -> dst: A,0]
        C2[Connection<br/>src: I,1 -> dst: A,0]
        C3[Connection<br/>src: I,0 -> dst: A,1]
        style C1 fill:#87CEEB
        style C2 fill:#87CEEB
        style C3 fill:#87CEEB
    end
    
    subgraph "Interface Layer - Management"
        IF[Interface<br/>endpoints: EP, ...<br/>connections: 0: C1, C2]
        style IF fill:#FFD700
    end
    
    IF --> EP
    IF --> C1
    IF --> C2
    IF --> C3
    
    Benefit1[✅ Single EP deduplicated<br/>across multiple uses]
    Benefit2[✅ Connections managed<br/>independently]
    Benefit3[✅ Add/remove connections<br/>without new endpoints]
    
    EP -.-> Benefit1
    C1 -.-> Benefit2
    C2 -.-> Benefit2
    IF -.-> Benefit3
```

## Data Flow Comparison

### Before: Tightly Coupled

```mermaid
sequenceDiagram
    participant Code
    participant EndPoint
    participant Deduplicator
    
    Code->>EndPoint: Create with refs=[[I,0]]
    EndPoint->>EndPoint: Initialize identity + refs
    Code->>EndPoint: freeze()
    EndPoint->>EndPoint: Freeze identity AND refs
    EndPoint->>Deduplicator: Store frozen object
    Note over Deduplicator: Can't reuse if refs differ!
    
    Code->>EndPoint: Create with refs=[[I,1]]
    EndPoint->>EndPoint: Initialize identity + DIFFERENT refs
    Code->>EndPoint: freeze()
    EndPoint->>Deduplicator: Store as NEW object
    Note over Deduplicator: Duplicate identity! ❌
```

### After: Decoupled

```mermaid
sequenceDiagram
    participant Code
    participant EndPoint
    participant Connection
    participant Interface
    participant Deduplicator
    
    Code->>EndPoint: Create (no refs!)
    EndPoint->>EndPoint: Initialize identity only
    Code->>EndPoint: freeze()
    EndPoint->>Deduplicator: Store frozen object
    Note over Deduplicator: Stored! ✅
    
    Code->>EndPoint: Create (same identity)
    EndPoint->>Deduplicator: Check for existing
    Deduplicator->>Code: Return SAME object! ✅
    
    Code->>Connection: Create(I,0 -> A,0)
    Code->>Connection: Create(I,1 -> A,0)
    Code->>Interface: add_connection(0, conn1)
    Code->>Interface: add_connection(0, conn2)
    Note over Interface: Manages relationships!
```

## Memory Efficiency Improvement

### Before

```
Memory Usage Example (10,000 similar endpoints with different connections):

EndPoint objects: 10,000 × 200 bytes = 2,000,000 bytes
├─ Identity data: 10,000 × 50 bytes  =   500,000 bytes (duplicated! ❌)
└─ Connection data: 10,000 × 150 bytes = 1,500,000 bytes

Total: ~2.0 MB with lots of duplication
```

### After

```
Memory Usage Example (10,000 similar endpoints with different connections):

EndPoint objects: 1 × 50 bytes = 50 bytes (deduplicated! ✅)
Connection objects: 10,000 × 100 bytes = 1,000,000 bytes
Interface overhead: ~50,000 bytes

Total: ~1.05 MB (47.5% reduction!)
```

## API Changes

### Endpoint Creation

**Before:**
```python
ep = EndPoint(DstRow.A, 0, EndPointClass.DST, "int", refs=[["I", 0]])
ep.connect(other_ep)
if ep.is_connected():
    refs = ep.refs
```

**After:**
```python
ep = EndPoint(DstRow.A, 0, EndPointClass.DST, "int")
# No refs, no connect() method

# Connection managed by Interface
interface = Interface([ep])
interface.add_connection(0, Connection(SrcRow.I, 0, DstRow.A, 0))
if interface.is_connected(0):
    conns = interface.get_connections(0)
```

### Interface Usage

**Before:**
```python
# Refs embedded in endpoint
interface = Interface([
    EndPoint(DstRow.A, 0, EndPointClass.DST, "int", refs=[["I", 0]]),
    EndPoint(DstRow.A, 1, EndPointClass.DST, "float", refs=[["I", 1]]),
])

# Access refs through endpoint
for ep in interface:
    for ref in ep.refs:
        row, idx = ref[0], ref[1]
```

**After:**
```python
# Endpoints and connections separate
interface = Interface(
    endpoints=[
        EndPoint(DstRow.A, 0, EndPointClass.DST, "int"),
        EndPoint(DstRow.A, 1, EndPointClass.DST, "float"),
    ],
    connections={
        0: [Connection(SrcRow.I, 0, DstRow.A, 0)],
        1: [Connection(SrcRow.I, 1, DstRow.A, 1)],
    }
)

# Access connections through interface
for idx, ep in enumerate(interface):
    for conn in interface.get_connections(idx):
        src_row, src_idx = conn.src_row, conn.src_idx
```

## Implementation Phases

```mermaid
gantt
    title Refactoring Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1
    Create Connection class     :p1a, 2025-11-03, 2h
    Update EndPoint (remove refs) :p1b, after p1a, 2h
    Add endpoint deduplication  :p1c, after p1b, 2h
    
    section Phase 2
    Add connections to Interface :p2a, after p1c, 3h
    Connection management API   :p2b, after p2a, 2h
    Backward compat layer       :p2c, after p2b, 2h
    
    section Phase 3
    Update CGraph               :p3a, after p2c, 3h
    Update executors            :p3b, after p3a, 2h
    Update all tests            :p3c, after p3b, 8h
    
    section Phase 4
    Remove compat layer         :p4a, after p3c, 1h
    Documentation               :p4b, after p4a, 2h
    Performance validation      :p4c, after p4b, 3h
```

## Validation Checklist

- [ ] All existing tests pass
- [ ] New connection tests added
- [ ] Deduplication working as expected
- [ ] Memory usage improved (benchmark)
- [ ] No performance regression
- [ ] Documentation updated
- [ ] Code review completed
