from typing import List
import pandas as pd

from .config import SEASON_FILES
from .utils import _pick_col, normalize_driver_code


def get_season_results(season: int) -> pd.DataFrame:
    if season not in SEASON_FILES:
        print("Supported seasons:", ", ".join(map(str, sorted(SEASON_FILES.keys()))))
        return pd.DataFrame()

    path = SEASON_FILES[season]
    try:
        raw = pd.read_csv(path)
    except FileNotFoundError:
        print(f"CSV file not found: {path}")
        return pd.DataFrame()

    race_name_col = _pick_col(raw, ["Track", "Race", "raceName", "Race Name"])
    driver_name_col = _pick_col(raw, ["Driver", "driver", "Name"])
    constructor_col = _pick_col(raw, ["Team", "Constructor", "Car"])
    position_col = _pick_col(raw, ["Position", "Pos", "position"])
    points_col = _pick_col(raw, ["Points", "points"])

    status_col = next((c for c in ["Time/Retired", "Time", "Status", "Result"] if c in raw.columns), None)

    rows: List[dict] = []
    race_order = (
        raw[race_name_col]
        .drop_duplicates()
        .reset_index(drop=True)
        .reset_index()
        .rename(columns={"index": "round"})
    )
    race_order["round"] += 1

    raw = raw.merge(race_order, on=race_name_col, how="left")

    for _, r in raw.iterrows():
        race_name = str(r[race_name_col]).strip()
        driver_name = str(r[driver_name_col]).strip()
        constructor = str(r[constructor_col]).strip()

        try:
            position = int(r[position_col])
        except Exception:
            position = 99

        try:
            points = float(r[points_col])
        except Exception:
            points = 0.0

        status = str(r[status_col]).strip() if status_col else ""

        rows.append(
            {
                "round": int(r["round"]),
                "race_name": race_name,
                "date": "",
                "driver_code": normalize_driver_code(driver_name),
                "driver_name": driver_name,
                "constructor": constructor,
                "position": position,
                "points": points,
                "status": status,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        print("No rows parsed from CSV. This usually means column names didn't match.")
        print("Open the CSV and check its headers.")
        return df

    df.sort_values(["round", "position"], inplace=True)
    return df
