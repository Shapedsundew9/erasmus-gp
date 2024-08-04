"""The problem module contains the classes and functions for the problem object."""
from hashlib import sha256


# The beginning
ABIOGENESIS_PROBLEM = sha256(b"Abiogenesis Problem").digest()
