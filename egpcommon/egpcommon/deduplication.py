"""De-duplication utilities for immutable objects."""

from egpcommon.object_deduplicator import ObjectDeduplicator

# Use the default 65536 size for signatures as these are frequently created.
signature_store = ObjectDeduplicator("Signature Store")

# Use 4096 for UUIDs as these are often the same.
uuid_store = ObjectDeduplicator("UUID Store", 2**12)

# Use 4096 for properties as these are often the same.
properties_store = ObjectDeduplicator("Properties Store", 2**12)

# 256 integers
int256_store = ObjectDeduplicator("Integer Store", 2**8)
