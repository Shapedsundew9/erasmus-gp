# GC Properties

| Name | Type | Bitfield | Default | Description |
|---|:-:|:-:|:-:|---|
| graph_type | uint | 3:0 | 0 | Valid ranges: [(0, 4)]. Graph type. 0 = Codon, 1 = Conditional, 2 = Empty, 3 = Standard, 4-15 = Reserved. |
| reserved1 | uint | 7:4 | 0 | Valid values: {0}. Reserved for future use. |
| constant | bool | 8 | False | Genetic code _always_ returns the same result. |
| deterministic | bool | 9 | True | Given the same inputs the genetic code will _always_ return the same result. |
| simplification | bool | 10 | False | The genetic code is eligible to be simplified by symbolic regression. |
| literal | bool | 11 | False | The output types are literals (which require special handling in some cases). |
| abstract | bool | 12 | False | At least one type in one interface is abstract. |
| reserved2 | uint | 63:13 | 0 | Valid values: {0}. Reserved for future use. |
