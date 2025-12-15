import numpy as np

def add_energy_percentages(df):
    """
    Adds:
      Net Carbs (g) (if Fiber exists, it subtracts them, because fiber does not have calories)
      Macro kcal (4-4-9, fiber adj)
      Carb % (net, 4-4-9), Protein % (4-4-9), Fat % (4-4-9)
      % Sugar in Carbs (if Sugar exists)
    """
    out = df.copy()

    if "Fiber" in out.columns:
        out["Net Carbs (g)"] = (out["Carbohydrates (g)"] - out["Fiber"]).clip(lower=0)
    else:
        out["Net Carbs (g)"] = out["Carbohydrates (g)"]

    out["Macro kcal (4-4-9, fiber adj)"] = (
        out["Net Carbs (g)"] * 4 +
        out["Protein (g)"] * 4 +
        out["Fat (g)"] * 9
    )

    # denominator used to calculate percentages below
    denom = out["Macro kcal (4-4-9, fiber adj)"].replace({0: np.nan})

    out["Carb % (net, 4-4-9)"] = (out["Net Carbs (g)"] * 4 / denom) * 100
    out["Protein % (4-4-9)"]   = (out["Protein (g)"] * 4 / denom) * 100
    out["Fat % (4-4-9)"]       = (out["Fat (g)"] * 9 / denom) * 100

    if "Sugar" in out.columns:
        out["% Sugar in Carbs"] = (out["Sugar"] / out["Carbohydrates (g)"].replace({0: np.nan})) * 100

    return out