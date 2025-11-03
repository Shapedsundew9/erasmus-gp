# Credit Assiognment

## PGSs

### Herditary Credit

Exponential Decay with Recency Bias. Assign credit that decays exponentially with genealogical distance, weighted by recency.

#### Advantages

- ✅ Mathematically principled (temporal difference learning)
- ✅ Naturally handles infinite recursion
- ✅ Prevents credit from exploding at deep levels
- ✅ Recent innovations valued more than ancient ones

```mermaid
graph TD
    PGC3["PGC Level 3<br/>Created PGC2"] 
    PGC2["PGC Level 2<br/>Created PGC1"]
    PGC1["PGC Level 1<br/>Created Solution"]
    SOL["Solution GC<br/>Fitness: 0.85"]
    
    PGC3 -.->|created| PGC2
    PGC2 -.->|created| PGC1
    PGC1 -.->|created| SOL
    
    SOL -->|Credit?| PGC1
    SOL -.->|Credit?| PGC2
    SOL -.->|Credit?| PGC3
    
    style SOL fill:#4CAF50
    style PGC1 fill:#FF9800
    style PGC2 fill:#2196F3
    style PGC3 fill:#9C27B0
```

```python
def calculate_pgc_credit(
    offspring_fitness: float,
    pgc_depth: int,  # How many levels up the PGC chain
    decay_rate: float = 0.5,  # Half-life per generation
    time_discount: float = 0.95  # Recency factor
) -> float:
    """
    Credit = fitness × decay^depth × time_discount^age
    
    Example:
    - Direct parent PGC (depth=1): 0.85 × 0.5^1 = 0.425
    - Grandparent PGC (depth=2): 0.85 × 0.5^2 = 0.2125
    - Great-grandparent (depth=3): 0.85 × 0.5^3 = 0.10625
    """
    return offspring_fitness * (decay_rate ** pgc_depth) * (time_discount ** age_in_generations)
```

### Sub-PGC Credit

Since PGCS have an internal fitness function, whenever they are run they can be assessed relative to their fitness function. And get credit. From that. However, for the wider context. Of the overall PGC. And its success. Credit needs to be given at some proportion.
