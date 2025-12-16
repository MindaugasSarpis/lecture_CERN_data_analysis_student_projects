import pandas as pd

def _contains_any(text: str, keywords: list[str]) -> bool:
    t = str(text).upper()
    return any(k.upper() in t for k in keywords)

def categorize_transactions(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    df = df.copy()
    df["category"] = config.get("unknown_category", "Miscellaneous")

    # Investments
    inv = config.get("investments", {})
    inv_kw = inv.get("keywords", [])
    inv_ibans = set(inv.get("ibans", []))
    df.loc[
        df["merchant"].apply(lambda s: _contains_any(s, inv_kw)) | df["iban"].isin(inv_ibans),
        "category"
    ] = "Investment"

    # Income: employers
    for emp in config.get("income", {}).get("employers", []):
        kws = emp.get("keywords", [])
        ibs = set(emp.get("ibans", []))
        mask = df["amount"] > 0
        if kws:
            mask &= df["merchant"].apply(lambda s: _contains_any(s, kws))
        if ibs:
            mask |= (df["iban"].isin(ibs) & (df["amount"] > 0))
        df.loc[mask, "category"] = "Income:Employer"

    # Income: students (multiples of 20 or IBANs)
    students_conf = config.get("income", {}).get("students", {})
    mult = students_conf.get("multiples_of", 20)
    st_ibans = set(students_conf.get("ibans", []))
    mask_students = (df["amount"] > 0) & ((df["amount"] % mult) == 0)
    if st_ibans:
        mask_students |= (df["iban"].isin(st_ibans) & (df["amount"] > 0))
    df.loc[mask_students, "category"] = "Income:Students"

    # Income: students cash
    cash_kw = config.get("income", {}).get("cash_students", {}).get("keyword", "")
    if cash_kw:
        df.loc[
            (df["amount"] > 0) & (df["description"].str.upper().str.contains(cash_kw.upper(), na=False)),
            "category"
        ] = "Income:Students:Cash"

    # Expense categories from keywords
    for cat, kws in config.get("categories", {}).items():
        mask = (df["amount"] < 0) & (
            df["merchant"].apply(lambda s: _contains_any(s, kws))
            | df["description"].apply(lambda s: _contains_any(s, kws))
        )
        df.loc[mask, "category"] = cat

    return df

def compute_income_sources(df: pd.DataFrame, config: dict) -> dict:
    inc = df[df["amount"] > 0].copy()
    res: dict[str, float] = {}
    res["Employer"] = float(inc[inc["category"] == "Income:Employer"]["amount"].sum())
    res["Students"] = float(inc[inc["category"] == "Income:Students"]["amount"].sum())
    res["Students:Cash"] = float(inc[inc["category"] == "Income:Students:Cash"]["amount"].sum())
    other = float(inc[~inc["category"].str.startswith("Income")]["amount"].sum())
    if abs(other) > 1e-9:
        res["Other"] = other
    return res
