import random
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np

from .config import WorldConfig, TERRAIN_PARAMS
from .agents import Prey, Predator
from .viz import plot_populations, plot_terrain_and_resources, animate_world

# Directory where this module lives; outputs go here by default
SCRIPT_DIR = Path(__file__).resolve().parent


def save_or_show(fig, filename: Optional[str], show: bool):
    if filename is not None:
        out_path = SCRIPT_DIR / filename
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
    if show:
        import matplotlib.pyplot as plt
        plt.show()
    else:
        import matplotlib.pyplot as plt
        plt.close(fig)


class World:
    def __init__(self, cfg: WorldConfig):
        self.cfg = cfg
        w, h = cfg.width, cfg.height
        self.area = w * h

        self.terrain = self._generate_terrain(w, h)

        self.max_resource = np.zeros((h, w), dtype=np.float32)
        self.regrowth_rate = np.zeros((h, w), dtype=np.float32)
        for y in range(h):
            for x in range(w):
                t = self.terrain[y, x]
                p = TERRAIN_PARAMS[t]
                self.max_resource[y, x] = cfg.base_max_resource * p["resource_scale"]
                self.regrowth_rate[y, x] = cfg.base_resource_regrowth_rate * p["regrowth_scale"]

        self.resources = np.random.uniform(0, self.max_resource, size=(h, w)).astype(np.float32)

        self.prey: List[Prey] = []
        self.predators: List[Predator] = []
        self._init_agents()

        self.prey_history: List[int] = []
        self.pred_history: List[int] = []

        self._anim = None

    def _generate_terrain(self, w: int, h: int) -> np.ndarray:
        noise = np.random.rand(h, w)
        kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], float)
        kernel /= kernel.sum()
        for _ in range(3):
            padded = np.pad(noise, 1, mode="edge")
            smoothed = np.zeros_like(noise)
            for y in range(h):
                for x in range(w):
                    smoothed[y, x] = (padded[y:y+3, x:x+3] * kernel).sum()
            noise = smoothed

        water_cut = random.uniform(0.10, 0.25)
        grass_cut = water_cut + random.uniform(0.25, 0.40)
        forest_cut = grass_cut + random.uniform(0.15, 0.30)
        forest_cut = min(forest_cut, 0.95)

        terrain = np.zeros((h, w), dtype=np.int8)
        for y in range(h):
            for x in range(w):
                v = noise[y, x]
                terrain[y, x] = (
                    0 if v < water_cut else
                    1 if v < grass_cut else
                    2 if v < forest_cut else
                    3
                )
        return terrain

    def _random_passable_cell(self) -> Tuple[int, int]:
        while True:
            x = random.randrange(self.cfg.width)
            y = random.randrange(self.cfg.height)
            if TERRAIN_PARAMS[self.terrain[y, x]]["passable"]:
                return x, y


    def _init_agents(self):
        c = self.cfg
        for _ in range(c.initial_prey):
            x, y = self._random_passable_cell()
            self.prey.append(Prey(x, y, c.prey_initial_energy, c.prey_max_age))
        for _ in range(c.initial_predators):
            x, y = self._random_passable_cell()
            self.predators.append(Predator(x, y, c.predator_initial_energy, c.predator_max_age))

    def _neighbors_within_radius(self, x: int, y: int, r: int) -> List[Tuple[int, int]]:
        w, h = self.cfg.width, self.cfg.height
        res = []
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.cfg.toroidal:
                    nx %= w; ny %= h
                if 0 <= nx < w and 0 <= ny < h and TERRAIN_PARAMS[self.terrain[ny, nx]]["passable"]:
                    res.append((nx, ny))
        return res

    def _density(self) -> float:
        return (len(self.prey) + len(self.predators)) / float(self.area)

    def step_environment(self):
        self.resources += self.regrowth_rate * (self.max_resource - self.resources)

    def _total_entities(self, extra_prey: int = 0, extra_pred: int = 0) -> int:
        return len(self.prey) + len(self.predators) + extra_prey + extra_pred

    def step_prey(self):
        random.shuffle(self.prey)
        new_prey: List[Prey] = []
        c = self.cfg
        density = self._density()
        roaming = density < c.roam_density_threshold

        for p in self.prey:
            if not p.alive:
                continue

            r = max(1, int(self.cfg.movement_radius))
            nb = self._neighbors_within_radius(p.x, p.y, r)
            if nb:
                if roaming or random.random() < c.random_move_chance:
                    p.x, p.y = random.choice(nb)
                else:
                    res_levels = np.array([self.resources[y, x] for x, y in nb])
                    best = res_levels.max()
                    mask = res_levels >= best * 0.9
                    candidates = [nb[i] for i, ok in enumerate(mask) if ok]
                    p.x, p.y = random.choice(candidates)

            t = TERRAIN_PARAMS[self.terrain[p.y, p.x]]
            move_cost = c.prey_base_move_cost * t["move_cost_scale"]
            p.step_age_and_energy(move_cost)
            if not p.alive:
                continue

            eat = min(c.prey_eat_amount, self.resources[p.y, p.x])
            self.resources[p.y, p.x] -= eat
            p.energy += eat

            if (p.energy >= c.prey_base_reproduce_threshold and
                    self._total_entities(extra_prey=len(new_prey) + 1) <= c.max_entities):
                p.energy -= c.prey_reproduce_cost
                new_prey.append(Prey(p.x, p.y, c.prey_initial_energy, c.prey_max_age))

            new_prey.append(p)

        max_prey = int(c.max_prey_density * self.area)
        if max_prey > 0 and len(new_prey) > max_prey:
            over = (len(new_prey) - max_prey) / float(max_prey)
            death_p = min(1.0, over * c.prey_overcrowd_mortality)
            new_prey = [p for p in new_prey if random.random() >= death_p]

        self.prey = new_prey

    def step_predators(self):
        c = self.cfg
        random.shuffle(self.predators)

        prey_grid = {}
        for p in self.prey:
            if p.alive:
                prey_grid.setdefault((p.x, p.y), []).append(p)

        density = self._density()
        roaming = density < c.roam_density_threshold

        moved_preds: List[Predator] = []
        for pred in self.predators:
            if not pred.alive:
                continue

            r = max(1, int(self.cfg.movement_radius))
            nb = self._neighbors_within_radius(pred.x, pred.y, r)
            if nb:
                if roaming or random.random() < c.random_move_chance:
                    pred.x, pred.y = random.choice(nb)
                else:
                    prey_cells = [xy for xy in nb if xy in prey_grid]
                    if prey_cells:
                        pred.x, pred.y = random.choice(prey_cells)
                    else:
                        pred.x, pred.y = random.choice(nb)

            t = TERRAIN_PARAMS[self.terrain[pred.y, pred.x]]
            move_cost = c.predator_base_move_cost * t["move_cost_scale"]
            pred.step_age_and_energy(move_cost)
            if pred.alive:
                moved_preds.append(pred)

        preds_by_cell = {}
        for pred in moved_preds:
            preds_by_cell.setdefault((pred.x, pred.y), []).append(pred)

        for cell, preds_here in preds_by_cell.items():
            prey_here = prey_grid.get(cell, [])
            live_prey = [p for p in prey_here if p.alive]
            if not live_prey:
                continue

            live_preds = [pr for pr in preds_here if pr.alive]
            if not live_preds:
                continue

            # predator PvP (fighting) removed per user request
            hunter = random.choice(live_preds)
            victims = [p for p in live_prey if p.alive]
            if not victims or not hunter.alive:
                continue
            victim = random.choice(victims)

            if random.random() < c.predator_hunt_death_chance:
                hunter.alive = False
            else:
                victim.alive = False
                hunter.energy += c.predator_eat_gain

        new_pred: List[Predator] = []
        for pred in moved_preds:
            if not pred.alive:
                continue
            if (pred.energy >= c.predator_base_reproduce_threshold and
                    self._total_entities(extra_pred=len(new_pred) + 1) <= c.max_entities):
                pred.energy -= c.predator_reproduce_cost
                new_pred.append(Predator(pred.x, pred.y, c.predator_initial_energy,
                                         c.predator_max_age))
            new_pred.append(pred)

        self.prey = [p for p in self.prey if p.alive]
        self.predators = new_pred

    def step(self, t: int):
        self.step_environment()
        self.step_prey()
        self.step_predators()
        self.prey_history.append(len(self.prey))
        self.pred_history.append(len(self.predators))

    def run(self):
        for t in range(self.cfg.max_steps):
            if not self.prey and not self.predators:
                print(f"All agents died out at step {t}.")
                break
            self.step(t)
        print("Simulation finished.")
        print(f"Final prey: {len(self.prey)}, predators: {len(self.predators)}")

    def write_final_traits(self, filename: str):
        # Removed: final traits output
        pass

    def plot_populations_and_trait(self, filename: Optional[str] = None, show: bool = True):
        plot_populations(self.prey_history, self.pred_history, filename=filename, show=show)

    def plot_terrain_and_resources(self, filename: Optional[str] = None, show: bool = True):
        plot_terrain_and_resources(self.terrain, self.resources, filename=filename, show=show)

    def _get_agent_positions(self):
        return (
            [p.x for p in self.prey], [p.y for p in self.prey],
            [p.x for p in self.predators], [p.y for p in self.predators],
        )

    def animate(self):
        animate_world(self)
