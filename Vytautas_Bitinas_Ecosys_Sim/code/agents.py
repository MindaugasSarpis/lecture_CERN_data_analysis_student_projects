from typing import Tuple

class Agent:
    """
    Base class for both Prey and Predator.
    """
    __slots__ = ("x", "y", "energy", "age", "max_age", "alive",
                 )

    def __init__(self, x: int, y: int, energy: float, max_age: int):
        self.x, self.y = x, y
        self.energy = energy
        self.age = 0
        self.max_age = max_age
        self.alive = True

    def step_age_and_energy(self, move_cost: float):
        """Advance age by 1 tick and subtract energy for this tick."""
        self.age += 1
        self.energy -= move_cost
        if self.energy <= 0 or self.age > self.max_age:
            self.alive = False


class Prey(Agent):
    """Herbivore agents: consume plant resources; lose energy each step."""
    pass


class Predator(Agent):
    """Carnivore agents: consume prey; lose energy each step."""
    pass
