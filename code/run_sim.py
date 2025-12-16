"""Run simulation as a separate process using a JSON config file.

Usage:
    python run_sim.py --config cfg.json [--animate]

This script loads the JSON config (keys should match `WorldConfig` names),
constructs a `WorldConfig` and runs the simulation (animated or batch).
"""
import argparse
import json
import sys
from pathlib import Path

# When run as a subprocess, ensure parent directory is on sys.path
# so we can import the code package
_code_parent = Path(__file__).resolve().parent.parent
if str(_code_parent) not in sys.path:
    sys.path.insert(0, str(_code_parent))

from .config import WorldConfig
from .world import World


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--animate", action="store_true")
    args = p.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter keys accepted by WorldConfig
    cfg = WorldConfig()
    for k, v in data.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)

    cfg.animate = bool(args.animate) or bool(data.get("animate", False))

    world = World(cfg)
    if cfg.animate:
        world.animate()
    else:
        world.run()
        world.plot_populations_and_trait("populations.png", show=True)
        world.plot_terrain_and_resources("terrain_resources.png", show=True)


if __name__ == "__main__":
    main()
