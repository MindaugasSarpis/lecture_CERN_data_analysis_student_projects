"""Entrypoint runner for the ecosystem simulation.

Minimal runner that ensures the script folder is on `sys.path`
and starts the simulation using the modular files in the same
directory (`config.py`, `world.py`, etc.).
"""

import sys
import random
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Import from the moved `code` package directly for robustness
from code.config import WorldConfig
import code.world as _world_mod
import code.viz as _viz_mod
from code.world import World

# Ensure world and viz modules save outputs to the repository root (top-level)
_world_mod.SCRIPT_DIR = SCRIPT_DIR
_viz_mod.SCRIPT_DIR = SCRIPT_DIR


def main():
    cfg = WorldConfig(
        width=random.randint(400, 700),
        height=random.randint(400, 700),
        initial_predators=random.randint(80, 250),
    )

    # keep prey = 2 * predators for the start
    cfg.initial_prey = 2 * cfg.initial_predators

    # enable animation by default so running the script shows the simulation
    cfg.animate = True

    print(f"World size: {cfg.width} x {cfg.height}")
    print(f"Initial prey: {cfg.initial_prey}, predators: {cfg.initial_predators}")
    print(f"Output directory: {SCRIPT_DIR}")

    world = World(cfg)

    if cfg.animate:
        world.animate()
        world.plot_populations_and_trait("populations.png", show=False)
        world.plot_terrain_and_resources("terrain_resources.png", show=False)
    else:
        world.run()
        world.plot_populations_and_trait("populations.png", show=True)
        world.plot_terrain_and_resources("terrain_resources.png", show=True)

    # final traits CSV output removed per user request
    print("Saved image outputs to the script directory.")


if __name__ == "__main__":
    main()