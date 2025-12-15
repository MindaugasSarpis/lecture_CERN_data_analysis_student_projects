import pandas as pd

def clean_transactions(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()

    # keep rows with date and amount
    df = df[pd.notnull(df["amount"])]
    df = df[pd.notnull(df["date"])]

    # dedupe by (date, |amount|, merchant, bank)
    key = df.apply(
        lambda r: (r["date"], abs(float(r["amount"])), str(r["merchant"]).strip().lower(), r["bank"]),
        axis=1,
    )
    df = df.loc[~key.duplicated()].copy()

    # normalize text
    for c in ["description", "merchant"]:
        df[c] = df[c].fillna("").astype(str)

    return df
