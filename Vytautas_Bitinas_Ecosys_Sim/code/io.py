from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent


def write_final_traits(path: str, prey_iter: Iterable, pred_iter: Iterable):
    out_path = SCRIPT_DIR / path
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("species,x,y,energy,age\n")
        for p in prey_iter:
            f.write(f"prey,{p.x},{p.y},{p.energy},{p.age}\n")
        for q in pred_iter:
            f.write(f"predator,{q.x},{q.y},{q.energy},{q.age}\n")
