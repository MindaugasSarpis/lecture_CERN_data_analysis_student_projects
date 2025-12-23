import pandas as pd

# Show all rows when printing DataFrames
pd.set_option("display.max_rows", None)

# Map season -> race results CSV (make sure these files exist)
SEASON_FILES = {
    2020: "data/formula1_2020season_raceResults.csv",
    2021: "data/formula1_2021season_raceResults.csv",
    2022: "data/Formula1_2022season_raceResults.csv",
    2023: "data/Formula1_2023season_raceResults.csv",
    2024: "data/Formula1_2024season_raceResults.csv",
    2025: "data/Formula1_2025Season_RaceResults.csv",
}
