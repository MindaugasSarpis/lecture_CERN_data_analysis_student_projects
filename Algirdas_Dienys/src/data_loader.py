import pandas as pd

def _pick_column(df, candidates, logical_name):
    """
    candidates: list[str] or str or None
    Returns the matched column name or None.
    """
    if candidates is None:
        return None
    if isinstance(candidates, str):
        candidates = [candidates]
    for c in candidates:
        if c in df.columns:
            return c
    return None

def load_daily_nutrition(path, colmap, start_date=None, end_date=None):
    """
    Reads nutrition CSV, renames columns to standard names, aggregates to daily totals.
    Standard output columns (if present):
      Date, Calories, Carbohydrates (g), Protein (g), Fat (g), Sugar, Fiber
    """
    df = pd.read_csv(path)

    # required logical fields
    required = ["date", "calories", "carbs", "protein", "fat"]
    selected = {}

    for key in required:
        cname = _pick_column(df, colmap.get(key), key)
        if cname is None:
            raise ValueError(f"Could not find required column for '{key}'. Available: {list(df.columns)}")
        selected[key] = cname

    # optional
    for key in ["sugar", "fiber"]:
        cname = _pick_column(df, colmap.get(key), key)
        if cname is not None:
            selected[key] = cname

    # rename into standard
    rename_to_standard = {
        selected["date"]:     "Date",
        selected["calories"]: "Calories",
        selected["carbs"]:    "Carbohydrates (g)",
        selected["protein"]:  "Protein (g)",
        selected["fat"]:      "Fat (g)",
    }
    if "sugar" in selected:
        rename_to_standard[selected["sugar"]] = "Sugar"
    if "fiber" in selected:
        rename_to_standard[selected["fiber"]] = "Fiber"

    df = df.rename(columns=rename_to_standard)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # date filter
    if start_date:
        df = df[df["Date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["Date"] <= pd.to_datetime(end_date)]

    # sum meals -> daily totals
    cols_to_sum = ["Calories", "Carbohydrates (g)", "Protein (g)", "Fat (g)"]
    if "Sugar" in df.columns:
        cols_to_sum.append("Sugar")
    if "Fiber" in df.columns:
        cols_to_sum.append("Fiber")

    daily = (
        df.groupby("Date")[cols_to_sum]
          .sum()
          .reset_index()
          .sort_values("Date")
          .reset_index(drop=True)
    )
    return daily

def load_home_time(path, colmap_home):
    """
    Reads home-time CSV and returns:
      Date, Time at home (hours)
    """
    df = pd.read_csv(path)

    date_col = _pick_column(df, colmap_home.get("date"), "date")
    time_col = _pick_column(df, colmap_home.get("time_home"), "time_home")

    if date_col is None or time_col is None:
        raise ValueError(f"Could not find date/time_home columns. Available: {list(df.columns)}")

    df = df.rename(columns={date_col: "Date", time_col: "Time at home (hours)"})
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # if duplicates, keep max time per day
    df = df.groupby("Date")[["Time at home (hours)"]].max().reset_index()
    return df

def merge_daily_with_home(daily_nut, home_df):
    return daily_nut.merge(home_df, on="Date", how="left")