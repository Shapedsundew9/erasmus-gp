# Worker Implementation Design

Each step in the Worker workflow is independent and implemented either within a python process or as a standalone web app. Both methods share code and only differ in the interfacing technology. The two versions exist to trade off between speed and scalability. The local python sub-process implementation has the advantage of shared memory and low overhead object passing which is advantageous in early development and early stage evolution when the fitness function may be far from the rate determining step. With more complex problems and thus more complex GC's the overhead of communication drops relative to the computational and memory resources needed for evolution and fitness function execution. Independent web apps with JSON REST API's are easily containerisable and scalable across HW resources using an orhesration layer like kubernetes.

## Python Sub-Processes

If the worker is configured with *config.type == "LOCAL"* then all pipeline stages, including the Fitness Executors, will be launched as a single python process (which may spawn subprocesses). This method of launching is much more efficient for simple problems built from codons or very simple GC's.
