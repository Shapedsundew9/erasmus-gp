# Genetic Code Properties

| Name | Type | Bitfield | Default | Description |
| --- | :-: | :-: | :-: | --- |
| gc_type | uint | 1:0 | 0 | Valid ranges: [(3,)]. GC type. |
| graph_type | uint | 5:2 | 0 | Valid ranges: [(7,)]. Graph type. |
| reserved1 | uint | 7:6 | 0 | Valid values: {0}. Reserved for future use. |
| constant | bool | 8 | False | Genetic code _always_ returns the same result. |
| deterministic | bool | 9 | True | Given the same inputs the genetic code will _always_ return the same result. |
| abstract | bool | 10 | False | At least one type in one interface is abstract. |
| side_effects | bool | 11 | False | The genetic code has side effects that are not related to the return value. |
| static_creation | bool | 12 | False | The genetic code was created by a deterministic PGC i.e. had no random element. |
| reserved2 | uint | 15:13 | 0 | Valid values: {0}. Reserved for future use. |
| gctsp | bitdict | 23:16 | N/A | See 'gctsp' definition table(s). |
| consider_cache | bool | 24 | False | Runtime property. The genetic code is eligible for result caching. e.g. with the functool `lru_cache`.Runtime profiling and resource availability will determine if it is actually cached. |
| reserved3 | uint | 31:25 | 0 | Valid values: {0}. Reserved for future 'Runtime properties'. |
| reserved4 | uint | 47:32 | 0 | Valid values: {0}. Reserved for future use. |
| Undefined | N/A | 48-55 | N/A | N/A |
| useless | bool | 56 | False | Valid values: {0}. Codon management system property. Useless codons can be removed with no functional impact. They can occur through mutation and be difficult to spot. |
| reserved5 | uint | 63:57 | 0 | Valid values: {0}. Reserved for future codon management use. |

## gctsp: gc_type = 0

| Name | Type | Bitfield | Default | Description |
| --- | :-: | :-: | :-: | --- |
| simplification | bool | 0 | False | The genetic code is eligible to be simplified by symbolic regression. |
| reserved7 | uint | 5:1 | 0 | Valid values: {0}. Reserved for future use. |
| python | bool | 6 | True | Codon code is Python. |
| psql | bool | 7 | False | Codon code is Postgres flavoured SQL. |

## gctsp: gc_type = 1

| Name | Type | Bitfield | Default | Description |
| --- | :-: | :-: | :-: | --- |
| literal | bool | 0 | False | The codon output type is a literal (which requires special handling in some cases). |
| reserved6 | uint | 5:1 | 0 | Valid values: {0}. Reserved for future use. |
| python | bool | 6 | True | Codon code is Python. |
| psql | bool | 7 | False | Codon code is Postgres flavoured SQL. |
