"""De-duplication utilities for immutable objects.

Module-level ObjectDeduplicator instances for commonly duplicated types.
Target rates are calculated from the break-even formula R = 120 / (S + 120)
where S is the object's memory size in bytes. See
``egpcommon/docs/object_deduplicator.md`` for the full analysis.
"""

from egpcommon.object_deduplicator import IntDeduplicator, ObjectDeduplicator

# SHA-256 signatures are 32 bytes → R = 120/(32+120) = 0.789
signature_store = ObjectDeduplicator("Signature", 2**16, 0.789)

# UUIDs are 16 bytes → R = 120/(16+120) = 0.882
uuid_store = ObjectDeduplicator("UUID", 2**12, 0.882)

# Properties are ints (28 bytes) → R = 120/(28+120) = 0.811
properties_store = ObjectDeduplicator("Properties", 2**12)

# Integers are 28 bytes → R = 120/(28+120) = 0.811
int_store = IntDeduplicator("Integer", 2**12)

# Strings vary; using default 0.811 (28-byte break-even) as a conservative baseline
string_store = ObjectDeduplicator("String", 2**10)

# Refs are signatures (32 bytes) → R = 0.789
ref_store = ObjectDeduplicator("Ref", 2**11, 0.789)

# Refs tuples vary; using default 0.811 as a conservative baseline
refs_store = ObjectDeduplicator("Refs", 2**11)
