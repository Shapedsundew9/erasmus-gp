# The Genetic Code Executor

- Creates the GC code to execute (including imports)
- Executes genetic codes and handles exceptions

## Writing GC Functions

GC functions are written to be between _limit/2_ and _limit_ functional lines in length where _limit_ is >= 4 and <= 2**15-1. The higher limit is pseudo arbitary (signed 16 bit max for efficient storage). In reality memory is the only limit but such large function sizes which may only differ by a few lines of code within them are ineffcient. The lower limit is to ensure at least 2 functional lines exist preventing a chain of functions calling just one function and the stack popping with no work being done. Sensible values of _limit_ trade off the overhead of function calling, readability and the stack depth. The default is 20 lines.

When a GC is written EGP breaks it down into sub-GC's as close to _limit_ as possible. The top level GC function may be < _limit/2_ lines long with a minimum of 2 lines when its GCA and GCB both are functions > _limit/2_ lines each. As evolution occurs what was a top level GC may get wrapped to be a sub-GC. If that, now sub, GC's executable was below the _limit/2_ minimum length then it will be assessed for merger in the top level GC and a new executable, not involving the existing one, may be created. The previous executable remains in the execution scope until the GC will no longer be used as an individual at which point it is deleted.

### Assessing a GC for Function Creation

Assessing a GC is done recursively (it is actaully implemented as a stack to allow for very deep GC's) using the following rules:

| # Lines      | Executable Exists | Operation       | Comments                                                                                                                                                              |
|:------------:|:-----------------:|:---------------:|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0            | True              | Error           | Having an executable but no lines is not possible.                                                                                                                    |
| < _limit/2_  | True              | Assess          | Was a "small" top level GC that can be merged into another.                                                                                                           |
| >= _limit/2_ | True              | Terminal        | Meets the criteria for a GC function. No need to analyse further.                                                                                                     |
| > _limit_    | True              | Error           | Should not be possible to have an executable with more than the limit number of lines.                                                                                |
| 0            | False             | Assess          | Has not been assessed yet.                                                                                                                                            |
| <= _limit_ | False             | Assess | Has previously been assessed and wrapped. Must be reassessed to build connection graph for incorpation in new executable. |
| > _limit_    | False             | Error           | This is a logic error is traversing the GC structure.                                                                                                                 |
