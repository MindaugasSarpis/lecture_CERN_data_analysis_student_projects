import json
import sys
import threading
from pathlib import Path

from code.config import WorldConfig
from code import world as world_mod
from code import viz as viz_mod
from code.world import World

SCRIPT_DIR = Path(__file__).resolve().parent.parent


def build_config_from_values(vals: dict) -> WorldConfig:
    cfg = WorldConfig()
    # set only known attributes
    for k, v in vals.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    return cfg


def run_simulation_thread(cfg: WorldConfig, animate: bool):
    try:
        # Ensure world and viz output to repo root, not code/
        world_mod.SCRIPT_DIR = SCRIPT_DIR
        viz_mod.SCRIPT_DIR = SCRIPT_DIR
        
        world = World(cfg)
        if animate:
            world.animate()
            world.plot_populations_and_trait('populations.png', show=False)
            world.plot_terrain_and_resources('terrain_resources.png', show=False)
        else:
            world.run()
            # Don't call show=True in background threads; just save
            world.plot_populations_and_trait('populations.png', show=False)
            world.plot_terrain_and_resources('terrain_resources.png', show=False)
        print(f'Outputs saved to: {SCRIPT_DIR}')
    except Exception as e:
        print(f'Error: {e}')
        raise


def run_in_background(cfg: WorldConfig, animate: bool):
    t = threading.Thread(target=run_simulation_thread, args=(cfg, animate), daemon=False)
    t.start()
