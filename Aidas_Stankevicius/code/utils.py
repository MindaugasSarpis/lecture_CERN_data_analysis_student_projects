from typing import List
import pandas as pd


def _pick_col(df: pd.DataFrame, candidates: List[str]) -> str:
    lower_map = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    raise KeyError(f"None of these columns exist: {candidates}\nAvailable: {list(df.columns)}")


def normalize_driver_code(name: str) -> str:
    return str(name).strip().upper().replace(" ", "_")
