"""Create the initial generation of individuals."""
from egppy.worker.evolution_queue import evolution_queue
from egppy.worker.fitness_queue import fitness_queue

def init_generation():
    evolution_queue()
    fitness_queue()
