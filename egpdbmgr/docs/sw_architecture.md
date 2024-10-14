# EGP Database Manager - Architecture

## Top Level

```mermaid
---
title: EGP DBM Architercture
---
flowchart TD
    db1[(Postgres
        GP/GL DB)]
    db2[(Postgres
        Archive DB)]
    dbm1["EGP DB Manager"]
    bu1[/"Archive Files"/]

    db1 <--> dbm1
    dbm1 <--> db2
    dbm1 <--> bu1
```

The EGP DB Manager is an independent process (container) that manages a postgres database for a storage role in EGP. The storage role (Gene Pool, Genomic Library, Archive) is defined by the DBM configuration upon creation.

The Postgres GP/GL DB should be more performant that the archive DB and is typically configured with more indexes & other parameters for speed. The Postgres Archive DB is used as a slower store of less frequently used GC's when the main DB reaches its size limit. When the Archive DB reaches its size limit unused GC's (the entire gene line of a poorly performing GC) are placed in to encrypted compressed database back up files.

## Initialisation

When the DBM intializes it will create or migrate the DB's as required and then respawn. This is to ensure any potential additional memory claim by these one-off processes are freed to the system before long term operation commences.

```mermaid
---
title: EGP DBM Initialisation
---
flowchart TD
    init1[Parse Configuration]
    init2[DB Discovery]
    init3{DB Exists}
    crt1[Create DB's]
    crt2{Higher Layer
        DB Exists?}
    crt3[Populate from
        Higher Layer]
    crt4[Populate from
        Installation]
    init4{Migration
        required?}
    init5[Run Archive
        Process once]
    init6[Lock DBs]
    init7[Backup DBs]
    init8[Migrate
        1 version]
    init9{Migration
        required ?}
    init10[Start
        operation]
    end1[Shutdown &
        respawn]
    st1[Sync to HL
        Process]
    st2[Archive
        Process]
    st3[REST API
        Process]
    st4[Analytics
        Process]

    init1 --> init2
    init2 --> init3
    init3 --> |Yes|init4
    init3 --> |No|crt1
    init4 --> |No|init5
    init5 --> init10
    init4 --> |Yes|init6
    init6 --> init7
    init7 --> init8
    init8 --> init9
    init9 --> |Yes|init8
    init9 --> |No|end1
    init10 --> st1
    init10 --> st2
    init10 --> st3
    init10 --> st4

    crt1 --> crt2
    crt2 --> |Yes|crt3
    crt2 --> |No|crt4
    crt3 --> end1
    crt4 --> end1
```

## Operation

### Archive Process

```mermaid
---
title: EGP DBM Archive Process
---
flowchart TD
    arc1{DB Size over
        limit?}
    arc2[Wait N
        seconds]
    arc3[Identify
        Candidates]
    arc4[Sync to HL
        on policy]
    arc5[Move to
        archive]
    arc6{Archive over
        limit?}
    arc7[Sync to HL
        on policy]
    arc8[Move to
        file]
        
    arc1 --> |No|arc2
    arc2 --> arc1
    arc1 --> |Yes|arc3
    arc3 --> arc4
    arc4 --> arc5
    arc5 --> arc6
    arc6 --> |No|arc1
    arc6 --> |Yes|arc7
    arc7 --> arc8
    arc8 --> arc1
```

### Sync to Higher Layer Process

### REST API Process

### Analytics Process

## Database Auxillary Tables

Besides the GC's in the main database table the DBM creates and manages some auxillary data tables to performance and analytics.

### DB Metadata

- UUID
- Version
- Created time
- Migration list (to version and timestamp)
- Host list (more than one if the DB moved hosts)
- Creator UUID
- Archive information
- HL Sync information
- Worker Session information

### Timeseries Analytics

- DB Size in GC's
- Number GC's archived
- Number GC's updated
- Number GC's sync'd
- Number problems
- Number populations
- Fitness distributions

etc.
