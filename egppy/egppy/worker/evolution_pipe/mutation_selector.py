"""Mutation selector module for evolution pipeline."""
from egppy.worker.evolution_pipe.mutation_queue import mutation_queue

def mutation_selector():
    """Select a mutation to apply."""
    mutation_queue()
