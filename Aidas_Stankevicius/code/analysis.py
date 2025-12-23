import pandas as pd


def get_driver_season(df: pd.DataFrame, driver_code: str) -> pd.DataFrame:
    driver_df = df[df["driver_code"] == driver_code].copy()
    driver_df.sort_values("round", inplace=True)
    driver_df["cumulative_points"] = driver_df["points"].cumsum()
    return driver_df


def get_season_champion(season_df: pd.DataFrame):
    totals = (
        season_df.groupby(["driver_code", "driver_name"], as_index=False)["points"].sum()
    )
    champion = totals.sort_values("points", ascending=False).iloc[0]
    return champion["driver_name"], champion["driver_code"], champion["points"]
