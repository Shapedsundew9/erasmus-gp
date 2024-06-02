# Abstraction and Isolation

Erasmus GP has a roadmap of function & optimisation to be implemented. To enable work to start with the most basic function and expand later the objects passed around are abstract, interfaces assumed asynchronous and functions as stateless as possible.

Any and all assumptions are coded into API's as assertions that can be enabled with the logging level.
Logging level *VERIFY* performs basic value and type checking.
Logging level *CONSISTENCY* does a more thourough check that all data in scope is sefl consistent.

# JSON and Dictionaries

Erasmus GP stores data in human readable JSON format where ever practical. This encourages the use of basic types and python dictionaries as viable
object base classes. Most Erasmus GP abstract base classes are subclassed from collections.abc MutableMapping.


