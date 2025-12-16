FINANCE_PROJECTdone — README
============================

Purpose
-------
Generate a monthly personal finance report from bank statements (CSV). The tool cleans and categorizes transactions, computes KPIs, renders charts, and writes an HTML report that opens automatically. Cleaned data are saved to `output/`.

Project layout (key paths)
--------------------------
- run.py — command-line entry point
- src/finance/ — pipeline, cleaning, categorization, KPIs, report rendering
- data/raw/ — put your input statement files here (*.csv)
- reports/ — generated reports: YYYY-MM_report.html (+ optional PDF)
- output/ — cleaned data exports: clean_transactions_YYYY-MM.csv/.parquet
- templates/ — HTML template(s) for report
- charts/ — chart images produced during a run
- requirements.txt — Python dependencies

Requirements
------------
- Python 3.10+
- CSV statements exported from your bank/fintech (UTF-8). If you have .xlsx, save as .csv.

Setup (first time)
------------------
Windows (PowerShell):
1) Create and activate a virtual environment, then install dependencies:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt

macOS / Linux:
1) Create and activate a virtual environment, then install dependencies:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt

Prepare your data
-----------------
1) Export statements as CSV from your bank(s).
2) Copy the files into data/raw/. Filenames can be anything, e.g.:
   - data/raw/swedbank_statement.csv
   - data/raw/revolut_statement.csv

What the pipeline expects (normalized columns)
----------------------------------------------
After internal normalization the dataset has these columns:
- date (YYYY-MM-DD)
- description (text)
- amount (number; expenses negative, income positive)
- currency (e.g., EUR)
- bank (source tag, e.g., "Swedbank", "Revolut")
- category (filled by categorization step)

Run a monthly report
--------------------
Windows (PowerShell):
1) Open a terminal in the project root:
   cd C:\Users\j.dubikaltis\.vscode\code\FINANCE_PROJECTdone
   .\.venv\Scripts\Activate.ps1
2) Run (example for November 2025 with two CSV files):
   py run.py --month 2025-11 `
     --csv "data/raw/swedbank_statement.csv" `
     --csv "data/raw/revolut_statement.csv"

Single-line PowerShell example:
   py run.py --month 2025-11 --csv "data/raw/swedbank_statement.csv" --csv "data/raw/revolut_statement.csv"

macOS / Linux:
   source .venv/bin/activate
   python run.py --month 2025-11 \
     --csv data/raw/swedbank_statement.csv \
     --csv data/raw/revolut_statement.csv

Command-line options
--------------------
--month YYYY-MM            Reporting month (required)
--csv PATH                 Input CSV file (repeat for multiple files)
--config PATH              Path to config.yaml (default: config.yaml)
--no-open                  Do not auto-open HTML report after generation

Output
------
- reports/YYYY-MM_report.html          Main HTML report (auto-opens)
- reports/YYYY-MM_report.pdf           PDF report (if enabled in render_report)
- output/clean_transactions_YYYY-MM.csv / .parquet
- charts/…                              PNG images for charts

Configuration (optional)
------------------------
config.yaml controls categorization and KPI rules. Example:

categories:
  groceries:
    match: ["lidl", "iki"]
  restaurants:
    match: ["kebabas", "mcdonald"]
income_sources:
  tutoring:
    match: ["euklido akademija"]
rules:
  case_insensitive: true
  first_match_wins: true
  default_category: "uncategorized"

Notes and assumptions
---------------------
- Amount sign convention: expenses negative, income positive. The normalizer flips signs if the source uses the opposite.
- Dates are parsed to YYYY-MM-DD; rows outside the selected --month are ignored.
- Only CSV inputs are supported. Save Excel files as CSV.
- Tested with Swedbank and Revolut exports.
- Data stay local; the tool does not send data to any external service.

Troubleshooting
---------------
- Nothing in the report for the month:
  Ensure CSV rows for that month exist and that the date column is parseable.
- "No CSVs provided":
  Add one or more --csv arguments.
- Report didn’t auto-open:
  Open the HTML manually from the reports/ folder.
- PowerShell cannot activate venv (execution policy):
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  Then .\.venv\Scripts\Activate.ps1
- UnicodeDecodeError or tokenizing errors:
  Re-export as UTF-8 CSV (comma separator, dot decimal).

Scheduling (optional)
---------------------
Windows Task Scheduler: run
  <path-to-python>\python.exe run.py --month YYYY-MM --csv <path> [--csv <path> ...]
on the 1st of each month. On macOS/Linux, use cron.

