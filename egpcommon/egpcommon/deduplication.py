"""De-duplication utilities for immutable objects."""

from egpcommon.object_deduplicator import IntDeduplicator, ObjectDeduplicator

# Use the default 65536 size for signatures as these are frequently created.
signature_store = ObjectDeduplicator("Signature", 2**16, 0.649)

# Use 4096 for UUIDs as these are often the same.
uuid_store = ObjectDeduplicator("UUID", 2**12, 0.649)

# Use 4096 for properties as these are often the same.
properties_store = ObjectDeduplicator("Properties", 2**12)

# 4096 integers
int_store = IntDeduplicator("Integer")
