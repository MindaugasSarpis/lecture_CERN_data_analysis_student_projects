Ecosystem Simulation
====================

Overview
--------
This is a lightweight ecosystem simulation with prey and predators on a terrain grid. The simulation models resource regrowth, prey grazing, predator hunting, reproduction and mortality. Trait-based behavior was removed; the code now uses fixed parameters for agents.

What this repo contains
Ecosystem Simulation
====================

Overview
--------
Lightweight ecosystem simulation with prey and predators on a 2D terrain grid. The model simulates resource regrowth, prey grazing, predator hunting, reproduction and mortality.

Repository contents
-------------------
- `Ecosystem Sim.py` — entrypoint runner (randomized world and populations).
- `gui.py` — Tkinter launcher to tweak parameters and run the simulation (recommended for casual use).
- `world.py` — simulation core: environment, stepping, agent logic, plotting and animation.
- `agents.py` — agent classes (`Prey`, `Predator`).
- `config.py` — `WorldConfig` dataclass with tunable parameters.
- `viz.py` — plotting and animation helpers.
- `run_sim.py` — helper used by the GUI to run animated simulations in a separate process (avoids Matplotlib/Tkinter thread issues).

Requirements
------------
- Python 3.8 or newer
- `numpy`, `matplotlib`

Quick setup
-----------
Windows (PowerShell):

```powershell
python -m pip install --upgrade pip
pip install numpy matplotlib
python gui.py
```

Ubuntu / Debian (bash):

```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
python3 -m pip install --user numpy matplotlib
python3 gui.py
```

Fedora (bash):

```bash
sudo dnf install python3 python3-pip python3-tkinter
python3 -m pip install --user numpy matplotlib
python3 gui.py
```

Notes:
- If `tkinter` is missing, install the OS package (`python3-tk` or `python3-tkinter`) as shown above.

Running from the command line
----------------------------
- To run the non-GUI entrypoint (randomized parameters):

```powershell
python "Ecosystem Sim.py"
```

Notes about the GUI and `run_sim.py`
-----------------------------------
- `gui.py` starts short/interactive simulations. For animated runs the GUI launches `run_sim.py` in a separate process so Matplotlib runs in that process's main thread. This prevents cross-thread GUI errors on Windows and Linux.
- If you delete `run_sim.py`, animated runs may raise warnings or fail; batch (non-animated) runs still work from the GUI.

Outputs
-------
- `populations.png` and `terrain_resources.png` are written to the project folder when the simulation finishes (batch runs or when animation completes and images are explicitly saved).

Troubleshooting
---------------
- If the GUI becomes unresponsive, reduce world size or use the "Run (Batch)" option.
- On Windows, if Matplotlib windows don't appear, ensure a GUI backend (TkAgg) is available. Using the GUI's animate option spawns a separate process which usually avoids backend issues.

Extending or customizing
------------------------
- Tweak parameters in `config.py` for different behaviors (energy, move cost, reproduction thresholds, resource regeneration).
- Modify `world.py` to change movement, hunting or reproduction mechanics.

License & credits
-----------------
This is a small demo project. No license included.
Made by Vytautas Bitinas.
