# Genetic Code Types

Genetic Code access and storage is critical to the performance of Erasmsus GP. Due to the large data volume is is not practical to have one unified type for a GC containing all of the GC data. There are five types of GC:

- **Embryonic Genetic Codes**, EGCs, contain the bare minimum data to create a GC. They are typically used as the 'working' type of EGP for creating new GC's. They are transient and never stored.
- **Common Genetic Codes**, CGCs, contain all EGC member plus additional data related to thier history that must be updated as they are used. They may be GGC's in higher layer stores but in the current context those specific field are not relevant e.g. they may be a GGC for a different problem space that as been inserted into a GGC in the current problem space. They may also 'just' be sub-GC's that do not provide a solution to a defined problem but have utillity in GGC's and PGCs sub-trees.
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
