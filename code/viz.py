from typing import Optional
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap

SCRIPT_DIR = Path(__file__).resolve().parent


def save_or_show(fig: plt.Figure, filename: Optional[str], show: bool):
    if filename is not None:
        out_path = SCRIPT_DIR / filename
        fig.savefig(out_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def plot_populations(prey_history, pred_history, filename: Optional[str] = None, show: bool = True):
    fig, ax1 = plt.subplots(figsize=(10, 4))
    steps = range(len(prey_history))
    ax1.plot(steps, prey_history, label="Prey", color="tab:green")
    ax1.plot(steps, pred_history, label="Predators", color="tab:red")
    ax1.set_xlabel("Time step")
    ax1.set_ylabel("Population size")
    ax1.legend(loc="upper left")
    ax1.grid(True)

    plt.title("Populations over time")
    fig.tight_layout()
    save_or_show(fig, filename, show)


def plot_terrain_and_resources(terrain, resources, filename: Optional[str] = None, show: bool = True):
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    # Remove 'water' color: mask out zeros (water) so they are not plotted
    cmap_terrain = ListedColormap(["yellowgreen", "darkgreen", "dimgray"])  # grass, forest, mountain
    masked = np.ma.masked_where(terrain == 0, terrain)
    cmap_terrain.set_bad(color="white")
    im0 = axes[0].imshow(masked, origin="lower", cmap=cmap_terrain, vmin=1, vmax=3)
    axes[0].set_title("Terrain\n1=grass,2=forest,3=mountain")
    fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)

    im1 = axes[1].imshow(resources, origin="lower", cmap="Greens")
    axes[1].set_title("Resource levels (final)")
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

    fig.tight_layout()
    save_or_show(fig, filename, show)


def animate_world(world, filename: Optional[str] = None):
    fig, ax = plt.subplots(figsize=(6, 6))
    im = ax.imshow(world.resources, origin="lower", cmap="Greens",
                   vmin=0, vmax=world.max_resource.max())
    px, py, qx, qy = world._get_agent_positions()
    scat_prey = ax.scatter(px, py, s=3, c="yellow", label="Prey")
    scat_pred = ax.scatter(qx, qy, s=4, c="red", label="Predator")
    ax.set_xlim(-0.5, world.cfg.width - 0.5)
    ax.set_ylim(-0.5, world.cfg.height - 0.5)
    ax.legend(loc="upper right")

    def update(frame):
        if not world.prey and not world.predators:
            ax.set_title("All agents died out")
            return scat_prey, scat_pred, im
        world.step(frame)
        im.set_array(world.resources)
        px, py, qx, qy = world._get_agent_positions()
        scat_prey.set_offsets(np.column_stack((px, py)) if px else np.empty((0, 2)))
        scat_pred.set_offsets(np.column_stack((qx, qy)) if qx else np.empty((0, 2)))
        ax.set_title(f"Step {frame} | Prey: {len(world.prey)} | Predators: {len(world.predators)}")
        return scat_prey, scat_pred, im

    anim = FuncAnimation(fig, update, frames=world.cfg.max_steps,
                         interval=world.cfg.anim_interval_ms, blit=False, repeat=False)
    plt.show()
    if filename:
        anim.save(str(SCRIPT_DIR / filename))
