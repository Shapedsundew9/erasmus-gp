# Genetic Code Types

Genetic Code access and storage is critical to the performance of Erasmsus GP. Due to the large data volume is is not practical to have one unified type for a GC containing all of the GC data. There are five types of GC:

- **Embryonic Genetic Codes**, EGCs, contain the bare minimum data to create a GC. They are typically used as the 'working' type of EGP for creating new GC's. They are transient and never stored allowing them to be implemented with the fastest implementation. The EGC implementation is designed around < 1000 EGC's simultaneously existing.
- **Common Genetic Codes**, CGCs, contain all EGC member plus additional data that is enough to full define the GC in the current context optimized for searching and filtering. CGC's form the local context for selectors to search and so must trade of in RAM storage space for search efficiency to provide an overall efficient local look up process. The CGC's implementation is designed around 1 million CGC's simultaneously existing.
- **General Genetic Codes**, GGCs, are fully defined solutions for the current problem context i.e. they have a fitness score and other problem specific data stored.
- **Physical Genetic Codes**, PGCs, are fully defined GCs that take other P, G or C, GC's and modify them. PGC's carry a lot of additional data defining their behaviour.
- **Universal Genetic Codes**, UGCs, may represent any GC, except an EGC, and include all initialization meta data. Typically UGC's are used to validate GC's pulled from a higher layer, initialize the local P, G or C, GC storage and set up the execution environment. They are versatile and transient.

```Mermaid
%% Genetic Code Type Inheritance Diagram
classDiagram
    Embryonic <|-- Common
    Common <|-- General
    Common <|-- Physical
    General <|-- Universal
    Physical <|-- Universal
```
