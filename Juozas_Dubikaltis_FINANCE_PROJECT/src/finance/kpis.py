from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# -----------------------
# CORE KPI AGGREGATES
# -----------------------

def compute_kpis(df: pd.DataFrame, config: Dict) -> Dict:
    income = float(df.loc[df["amount"] > 0, "amount"].sum())
    expenses = float(df.loc[df["amount"] < 0, "amount"].sum())
    invested = float(df.loc[df["category"] == "Investment", "amount"].sum())
    return {"total_income": income, "total_expenses": expenses, "total_invested": abs(invested)}


# -----------------------
# TABLE SUMMARIES
# -----------------------

def expense_category_summary(df: pd.DataFrame) -> List[Dict]:
    exp = df[df["amount"] < 0].copy()
    if exp.empty:
        return []
    by_sum = exp.groupby("category", dropna=False)["amount"].sum().abs().sort_values(ascending=False)
    by_count = exp.groupby("category", dropna=False)["amount"].count()
    total = float(by_sum.sum()) or 0.0
    rows: List[Dict] = []
    for cat, eur in by_sum.items():
        cnt = int(by_count.get(cat, 0))
        pct = float(eur) / total * 100 if total else 0.0
        rows.append({"category": str(cat), "eur": float(eur), "pct": pct, "tx_count": cnt})
    return rows


def income_source_summary(df: pd.DataFrame) -> List[Dict]:
    inc = df[df["amount"] > 0].copy()
    if inc.empty:
        return []
    buckets = {
        "Employer": ["Income:Employer"],
        "Students": ["Income:Students"],
        "Students:Cash": ["Income:Students:Cash"],
        "Other": [],
    }
    totals: Dict[str, float] = {k: 0.0 for k in buckets}
    all_bucket_cats: List[str] = []
    for label, cats in buckets.items():
        if cats:
            val = float(inc[inc["category"].isin(cats)]["amount"].sum())
            totals[label] = val
            all_bucket_cats.extend(cats)
    other_val = float(inc[~inc["category"].isin(all_bucket_cats)]["amount"].sum())
    totals["Other"] = other_val
    grand = sum(totals.values()) or 0.0
    rows: List[Dict] = []
    for label, val in totals.items():
        if abs(val) < 1e-9:
            continue
        pct = float(val) / grand * 100 if grand else 0.0
        rows.append({"source": label, "eur": float(val), "pct": pct})
    rows.sort(key=lambda r: r["eur"], reverse=True)
    return rows


def misc_details(df: pd.DataFrame, limit: int = 50) -> List[Dict]:
    misc = df[(df["amount"] < 0) & (df["category"] == "Miscellaneous")].copy()
    if misc.empty:
        return []
    misc = misc.sort_values("amount")
    out: List[Dict] = []
    for _, r in misc.head(limit).iterrows():
        out.append({
            "date": str(r["date"]),
            "merchant": str(r["merchant"]),
            "description": str(r["description"]),
            "eur": float(abs(r["amount"])),
        })
    return out


def top_merchants_table(df: pd.DataFrame, n: int = 15) -> List[Dict]:
    exp = df[df["amount"] < 0].copy()
    if exp.empty:
        return []
    g = exp.groupby("merchant", dropna=False)["amount"].agg(sum="sum", cnt="count").reset_index()
    g["abs_sum"] = g["sum"].abs()
    g = g.sort_values("abs_sum", ascending=False).drop(columns=["abs_sum"])
    rows: List[Dict] = []
    for rec in g.head(n).to_dict(orient="records"):
        rows.append({"merchant": rec["merchant"], "sum": float(rec["sum"]), "cnt": int(rec["cnt"])})
    return rows


# -----------------------
# CHARTS
# -----------------------

def _reports_dir() -> Path:
    p = Path("reports")
    p.mkdir(parents=True, exist_ok=True)
    return p


def category_pie_chart(df: pd.DataFrame, month_str: str, hide_labels: bool = False) -> str:
    reports_dir = _reports_dir()
    out_path = reports_dir / f"{month_str}_expenses_pie.png"
    exp = df[df["amount"] < 0].copy()
    if exp.empty:
        plt.figure()
        plt.title("No expenses")
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close()
        return out_path.name
    by_cat = exp.groupby("category")["amount"].sum().abs().sort_values(ascending=False)
    labels = list(by_cat.index)
    sizes = np.array(list(by_cat.values), dtype=float)
    total = float(sizes.sum()) or 0.0
    plt.figure(figsize=(6, 6))
    if hide_labels:
        wedges, _ = plt.pie(sizes, labels=None, startangle=90)
        legend_labels = labels  # names only
    else:
        if len(labels) <= 5:
            wedges, _, _ = plt.pie(sizes, labels=None, autopct="%1.1f%%", startangle=90)
            legend_labels = [f"{lab} — {val:.2f} EUR" for lab, val in zip(labels, sizes, strict=False)]
        else:
            wedges, _ = plt.pie(sizes, labels=None, startangle=90)
            legend_labels = []
            for lab, val in zip(labels, sizes, strict=False):
                pct = (val / total * 100) if total else 0.0
                legend_labels.append(f"{lab} — {val:.2f} EUR ({pct:.1f}%)")
    plt.title(f"Expenses by Category — {month_str}")
    plt.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return out_path.name


def income_pie_chart(df: pd.DataFrame, month_str: str, hide_labels: bool = False) -> str:
    reports_dir = _reports_dir()
    out_path = reports_dir / f"{month_str}_income_pie.png"
    inc = df[df["amount"] > 0].copy()
    if inc.empty:
        plt.figure()
        plt.title("No income")
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close()
        return out_path.name
    def bucket(row_cat: str) -> str:
        if row_cat == "Income:Employer": return "Employer"
        if row_cat == "Income:Students": return "Students"
        if row_cat == "Income:Students:Cash": return "Students:Cash"
        return "Other"
    inc["bucket"] = inc["category"].astype(str).map(bucket)
    by_b = inc.groupby("bucket")["amount"].sum()
    labels = list(by_b.index)
    sizes = np.array(list(by_b.values), dtype=float)
    plt.figure(figsize=(6, 6))
    if hide_labels:
        wedges, _ = plt.pie(sizes, labels=None, startangle=90)
        legend_labels = labels
    else:
        wedges, _, _ = plt.pie(sizes, labels=None, autopct="%1.1f%%", startangle=90)
        legend_labels = [f"{lab} — {val:.2f} EUR" for lab, val in zip(labels, sizes, strict=False)]
    plt.title(f"Income by Source — {month_str}")
    plt.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return out_path.name


def investment_pie_chart(df: pd.DataFrame, month_str: str, hide_labels: bool = False) -> str:
    reports_dir = _reports_dir()
    out_path = reports_dir / f"{month_str}_investment_pie.png"
    inv = df[df["category"] == "Investment"].copy()
    if inv.empty:
        plt.figure()
        plt.title("No investments")
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close()
        return out_path.name
    inv["label"] = inv["merchant"].fillna(inv["description"]).astype(str)
    by_lab = inv.groupby("label")["amount"].sum().abs().sort_values(ascending=False)
    labels = list(by_lab.index)
    sizes = np.array(list(by_lab.values), dtype=float)
    plt.figure(figsize=(6, 6))
    if hide_labels:
        wedges, _ = plt.pie(sizes, labels=None, startangle=90)
        legend_labels = labels
    else:
        wedges, _, _ = plt.pie(sizes, labels=None, autopct="%1.1f%%", startangle=90)
        legend_labels = [f"{lab} — {val:.2f} EUR" for lab, val in zip(labels, sizes, strict=False)]
    plt.title(f"Investments — {month_str}")
    plt.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return out_path.name


def daily_spend_chart(df: pd.DataFrame, month_str: str, hide_values: bool = False) -> Tuple[str, float]:
    reports_dir = _reports_dir()
    out_path = reports_dir / f"{month_str}_daily_spending.png"
    mask = (df["amount"] < 0) & (df["category"] != "Investment")
    exp = df[mask].copy()
    if exp.empty:
        plt.figure(figsize=(10, 3))
        plt.title("No daily spending data (excl. investments)")
        plt.savefig(out_path, dpi=150, bbox_inches="tight")
        plt.close()
        return out_path.name, 0.0
    exp["date"] = pd.to_datetime(exp["date"], errors="coerce")
    daily = exp.groupby("date")["amount"].sum().abs().sort_index()
    month_period = pd.Period(month_str)
    first_day = month_period.to_timestamp()
    last_day = (month_period + 1).to_timestamp() - pd.Timedelta(days=1)
    all_days = pd.date_range(first_day, last_day, freq="D")
    daily_full = daily.reindex(all_days, fill_value=0.0)
    avg_daily = float(daily_full.mean())
    x_vals = np.arange(len(all_days))
    day_labels = [d.day for d in all_days]
    heights = daily_full.values
    plt.figure(figsize=(14, 4))
    plt.bar(x_vals, heights)
    plt.xticks(x_vals, day_labels, rotation=0)
    plt.xlabel("Day of month")
    plt.ylabel("" if hide_values else "EUR spent")
    if hide_values:
        plt.gca().set_yticklabels([])
    plt.title(f"Daily spending (excl. investments) — {month_str}")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    return out_path.name, avg_daily
