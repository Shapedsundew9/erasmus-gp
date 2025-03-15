# Genetic Code Properties

| Name | Type | Bitfield | Default | Description |
|---|:-:|:-:|:-:|---|
| gc_type | uint | 1:0 | 0 | Valid ranges: [(2,)]. Graph type. 0 = Codon, 1 = Ordinary, 2 & 3 = Reserved. |
| graph_type | uint | 5:2 | 0 | Valid ranges: [(3,)]. Graph type. 0 = Conditional, 1 = Empty, 2 = Standard, 3-15 = Reserved. |
| reserved1 | uint | 7:6 | 0 | Valid values: {0}. Reserved for future use. |
| constant | bool | 8 | False | Genetic code _always_ returns the same result. |
| deterministic | bool | 9 | True | Given the same inputs the genetic code will _always_ return the same result. |
| abstract | bool | 10 | False | At least one type in one interface is abstract. |
| reserved2 | uint | 14:11 | 0 | Valid values: {0}. Reserved for future use. |
| Undefined | N/A | 15 | N/A | N/A |
| gctsp | bitdict | 23:16 | N/A | See 'gctsp' definition table(s). |
| reserved3 | uint | 63:24 | 0 | Valid values: {0}. Reserved for future use. |

## gctsp: graph_type = 0

| Name | Type | Bitfield | Default | Description |
|---|:-:|:-:|:-:|---|
| simplification | bool | 0 | False | The genetic code is eligible to be simplified by symbolic regression. |

## gctsp: graph_type = 1

| Name | Type | Bitfield | Default | Description |
|---|:-:|:-:|:-:|---|
| literal | bool | 0 | False | The codon output type is a literal (which requires special handling in some cases). |
