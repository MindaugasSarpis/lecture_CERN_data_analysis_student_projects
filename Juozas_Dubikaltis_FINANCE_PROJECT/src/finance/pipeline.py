from pathlib import Path
from typing import List

import pandas as pd
import yaml
import webbrowser

from .datasource.csv_source import CsvSource
from .io_normalize import normalize_any_bank
from .cleaning import clean_transactions
from .categorize import categorize_transactions, compute_income_sources
from .kpis import (
    compute_kpis,
    top_merchants_table,
    category_pie_chart,
    income_pie_chart,
    investment_pie_chart,
    expense_category_summary,
    income_source_summary,
    misc_details,
    daily_spend_chart,
)
from .report import render_report


def run_monthly_report(
    month_str: str,
    csv_paths: List[Path] | None,
    config_path: Path,
    presentation: bool = False,   # NEW
) -> str:
    month = pd.to_datetime(f"{month_str}-01")
    month_start = month.replace(day=1)
    next_month = month_start + pd.offsets.MonthBegin(1)
    month_end = next_month - pd.Timedelta(days=1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    if not csv_paths:
        raise SystemExit("No CSVs provided. Use --csv data/raw/*.csv")

    ds = CsvSource(csv_paths)
    raw_df = ds.fetch()

    df = normalize_any_bank(raw_df)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    mdf = df[(df["date"] >= month_start) & (df["date"] <= month_end)].copy()

    mdf = clean_transactions(mdf, config)
    mdf = categorize_transactions(mdf, config)

    kpis = compute_kpis(mdf, config)

    # charts: hide labels/values when presentation=True
    expenses_path = category_pie_chart(mdf, month_str, hide_labels=presentation)
    income_path = income_pie_chart(mdf, month_str, hide_labels=presentation)
    investment_path = investment_pie_chart(mdf, month_str, hide_labels=presentation)
    daily_path, avg_daily = daily_spend_chart(mdf, month_str, hide_values=presentation)
    kpis["avg_daily_spend"] = avg_daily

    charts = {
        "expenses": expenses_path,
        "income": income_path,
        "investments": investment_path,
        "daily": daily_path,
    }

    income_sources = compute_income_sources(mdf, config)
    cat_summary = expense_category_summary(mdf)
    inc_summary = income_source_summary(mdf)
    misc_rows = misc_details(mdf)
    merchants = top_merchants_table(mdf)

    source_summary = "n/a"
    if "bank" in mdf.columns:
        counts = mdf.groupby("bank")["amount"].count().to_dict()
        source_summary = ", ".join(f"{bank}: {cnt} tx" for bank, cnt in counts.items()) or "n/a"

    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_html = reports_dir / f"{month_str}_report.html"
    out_pdf = reports_dir / f"{month_str}_report.pdf"

    render_report(
        month=month_str,
        kpis=kpis,
        charts=charts,
        top_merchants=merchants,
        income_sources=income_sources,
        source_summary=source_summary,
        out_html=out_html,
        out_pdf=out_pdf,
        cat_summary=cat_summary,
        inc_summary=inc_summary,
        misc_rows=misc_rows,
        presentation=presentation,   # NEW
    )

    Path("output").mkdir(parents=True, exist_ok=True)
    mdf.to_parquet(Path("output") / f"clean_transactions_{month_str}.parquet", index=False)
    mdf.to_csv(Path("output") / f"clean_transactions_{month_str}.csv", index=False)

    try:
        webbrowser.open(out_html.resolve().as_uri(), new=2)
    except Exception as e:
        print(f"Could not auto-open the report: {e}")

    return str(out_html.resolve())
