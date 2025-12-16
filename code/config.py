from dataclasses import dataclass

# Terrain constants
TERRAIN_WATER = 0
TERRAIN_GRASS = 1
TERRAIN_FOREST = 2
TERRAIN_MOUNTAIN = 3

TERRAIN_PARAMS = {
    TERRAIN_WATER:   dict(name="water",   passable=False, resource_scale=0.0, regrowth_scale=0.0, move_cost_scale=100.0),
    TERRAIN_GRASS:   dict(name="grass",   passable=True,  resource_scale=1.0, regrowth_scale=1.0, move_cost_scale=1.0),
    TERRAIN_FOREST:  dict(name="forest",  passable=True,  resource_scale=2.2, regrowth_scale=0.8, move_cost_scale=1.8),
    TERRAIN_MOUNTAIN:dict(name="mountain",passable=False, resource_scale=0.0, regrowth_scale=0.0, move_cost_scale=100.0),
}


@dataclass
class WorldConfig:
    # Grid size (cells)
    width: int = 80
    height: int = 80

    # Initial populations
    initial_prey: int = 1500
    initial_predators: int = 300

    # Resources
    base_max_resource: float = 8.0
    base_resource_regrowth_rate: float = 0.09

    # Prey parameters
    prey_initial_energy: float = 10.0
    prey_base_move_cost: float = 0.27
    prey_eat_amount: float = 3.2
    prey_base_reproduce_threshold: float = 22.0
    prey_reproduce_cost: float = 9.0
    prey_max_age: int = 35

    # Predator parameters
    predator_initial_energy: float = 25.0
    predator_base_move_cost: float = 0.7
    predator_eat_gain: float = 14.0
    predator_base_reproduce_threshold: float = 38.0
    predator_reproduce_cost: float = 20.0
    predator_max_age: int = 80

    # Population & risk controls
    max_prey_density: float = 0.25
    prey_overcrowd_mortality: float = 0.9
    predator_hunt_death_chance: float = 0.04
    max_entities: int = 10_000
    roam_density_threshold: float = 0.01
    random_move_chance: float = 0.2

    # Simulation control
    max_steps: int = 1000
    toroidal: bool = True

    # Movement (global fixed radius)
    movement_radius: int = 1

    # Visualization
    animate: bool = False
    anim_interval_ms: int = 50
