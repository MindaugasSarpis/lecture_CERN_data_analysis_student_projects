import os
import pandas as pd

from src.data_loader import load_daily_nutrition, load_home_time, merge_daily_with_home
from src.features import add_energy_percentages
from src.scoring import compute_daily_scores
from src.plots import scatter_with_line, score_histogram

import config.config as config

def main():
    os.makedirs(config.OUTDIR, exist_ok=True)

    # ---- load nutrition ----
    df_daily = load_daily_nutrition(
        config.NUTRITION_CSV,
        config.NUT_COLS,
        start_date=config.START_DATE,
        end_date=config.END_DATE
    )

    # ---- optional home-time merge ----
    has_home = False
    if config.HOME_TIME_CSV:
        try:
            df_home = load_home_time(config.HOME_TIME_CSV, config.HOME_COLS)
            df_daily = merge_daily_with_home(df_daily, df_home)
            has_home = "Time at home (hours)" in df_daily.columns
        except FileNotFoundError:
            has_home = False

    # ---- features (fiber-aware macro %) ----
    df_daily = add_energy_percentages(df_daily)

    # ---- plots: calories vs carbs/protein/fat ----
    scatter_with_line(df_daily, "Carbohydrates (g)", "Calories",
                      outpath=f"{config.OUTDIR}/calories_vs_carbs.png")
    scatter_with_line(df_daily, "Protein (g)", "Calories",
                      outpath=f"{config.OUTDIR}/calories_vs_protein.png")
    scatter_with_line(df_daily, "Fat (g)", "Calories",
                      outpath=f"{config.OUTDIR}/calories_vs_fat.png")

    # ---- home-time dependent plots (only if available) ----
    if has_home:
        if "% Sugar in Carbs" in df_daily.columns:
            scatter_with_line(df_daily, "Time at home (hours)", "% Sugar in Carbs",
                              outpath=f"{config.OUTDIR}/sugar_pct_in_carbs_vs_home.png")

        scatter_with_line(df_daily, "Time at home (hours)", "Calories",
                          outpath=f"{config.OUTDIR}/calories_vs_home.png")
        scatter_with_line(df_daily, "Time at home (hours)", "Carb % (net, 4-4-9)",
                          outpath=f"{config.OUTDIR}/carb_pct_vs_home.png")
        scatter_with_line(df_daily, "Time at home (hours)", "Protein % (4-4-9)",
                          outpath=f"{config.OUTDIR}/protein_pct_vs_home.png")
        scatter_with_line(df_daily, "Time at home (hours)", "Fat % (4-4-9)",
                          outpath=f"{config.OUTDIR}/fat_pct_vs_home.png")

    # ---- scoring ----
    df_scored = compute_daily_scores(df_daily, config.SCORE_TARGETS)
    df_scored.to_csv(f"{config.OUTDIR}/df_daily_scored.csv", index=False)

    # ---- histogram ----
    score_histogram(df_scored, outpath=f"{config.OUTDIR}/score_histogram.png")

    print(f"Done. Outputs saved to: {config.OUTDIR}/")

if __name__ == "__main__":
    main()