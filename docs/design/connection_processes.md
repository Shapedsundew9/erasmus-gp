# Connection Processes

The problem of structuring and implementing the fundamental operations of CGraph manipulation has proven challenging. Specifically, determining the necessity and prioritization of connection creation for graph stabilization has been a persistent difficulty. This complexity arises from the existence of four distinct Connection Processes, each corresponding to a different mechanism for generating new Genetic Code.

## Definitions

**Compatible Endpoint Types** (also known as Compatible Connections): These are source-destination pairs of endpoint types where the source type is identical to or a descendant of the destination type (e.g., `int` (source) → `Integral` (destination)). These are also known as upcast connections. Upcast comes from the fact that inheritance trees are inverted \- the root is “up” in the inheritance diagram. This is a quirk of computer science conventions.  
**Downcast Endpoint Types** (also known as Downcast Connections): These constitute a superset of Compatible Endpoint Types, including pairs where the source type is an ancestor of the destination type. In this latter case, compatibility with the destination interface's function is not guaranteed but remains possible.  
**Select**: This refers to the act of choosing a source endpoint for connection. The selection algorithm is, by definition, arbitrary. In practice, numerous variations may exist, ranging from a default random selection of any source endpoint meeting the criteria to an optimized procedure specific to a particular line of Genetic Codes. Selection is an evolved function.Introducing the Concept of Primary Sources

Within a standard graph, each destination interface possesses a primary source interface. Other graph types lack this designation. A primary source interface is a preferred source among those to which a standard graph destination interface may connect. This preference is intended to encourage the formation of the prescribed code structure in standard CGraphs. If a compatible type connection is feasible between a destination and a primary source, at least one such connection is mandatory. The required connection between a primary source and a destination is termed a **Primary Connection**.

| Destination Row | Primary Source Row | Comment |
| ----- | ----- | ----- |
| Ad | Is |  |
| Bd | As |  |
| Od | Bs |  |

## The Four Connection Processes

1. **Create (Empty GC Filling):** A standard CGraph begins with predefined, immutable `Is` and `Od` interfaces, and no connections exist between any internal interfaces.  
   1. For each destination interface, in the order Ad, Bd, Od:  
      1. Select a compatible primary source endpoint.  
      2. If no compatible connection exists, select a valid primary source endpoint.  
      3. If a connection can be established, create it.  
         1. (Otherwise, the operation is a no-op.)  
2. **Wrap:** The resultant Genetic Code's (`GC`) `Is` and `Od` interfaces are defined by the input and output interfaces of GCA and GCB. Internal interfaces are directly connected between valid source and destination pairs.  
   1. For each destination interface, in the order Ad, Bd, Od, if there are unconnected endpoints.  
      1. If no primary connection is present:  
         1. Select a compatible primary source endpoint.  
         2. If no compatible connection exists, select a valid primary source endpoint.  
         3. If a connection can be established, create it.  
            1. (Otherwise, the operation is a no-op.)  
3. **Insertion:** Insertion is a meta-step that yields an RGC, and potentially an FGC, that is functionally identical to the original target TGC, but unstable due to the IGC's IO interfaces lacking connections. For the GC (RGC or FGC) containing the IGC:  
   1. Select a compatible primary source endpoint for the IGC input (destination) interface.  
   2. If no compatible connection exists, select a valid primary source endpoint.  
   3. If a connection can be established, create it.  
      1. (Otherwise, the operation is a no-op.)  
   4. Identify the destination interface(s) for which the IGC output serves as the primary source.  
   5. For each identified interface:  
      1. For each unconnected endpoint:  
         1. Select a compatible primary source endpoint.  
         2. If no compatible connection exists, select a valid primary source endpoint.  
         3. If a connection can be established, create it and exit the inner loop.  
            1. (Otherwise, the operation is a no-op.)  
      2. If no primary connection has been established:  
         1. For each connected endpoint:  
            1. Select a valid primary source endpoint.  
            2. If no compatible connection exists, select a valid primary source endpoint.  
            3. If a connection can be established, sever the existing connection, create a new connection to the primary source, and exit the inner loop.  
               1. (Otherwise, the operation is a no-op.)  
4. **Crossover:** Cross-over occurs when GCA or GCB are replaced, potentially altering the interface for their respective row.  
   1. If the interface of the new GCx differs from the one it replaced:  
      1. For both destination and source interfaces of the new row:  
         1. For each endpoint:  
            1. Connect the endpoint to the same source/destination defined by the connection that previously occupied this position, provided it is valid. (Invalid positions will be skipped.)  
      2. Execute the insertion connection process.
