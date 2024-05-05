"""Mutation Queue module for evolution pipeline."""
from egppy.worker.evolution_pipe.mutation_executor import mutation_executor

def mutation_queue():
    """Queue the mutation."""
    mutation_executor()