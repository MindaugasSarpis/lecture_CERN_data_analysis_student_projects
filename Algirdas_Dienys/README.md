# Nutrition & Lifestyle Analysis Project

This project provides a reusable and configurable Python pipeline to analyze daily nutrition data,
optionally combined with lifestyle data (time spent at home).

The pipeline is designed for reproducibility, flexibility, and easy adaptation to different
CSV formats (e.g. MyFitnessPal exports).

---

## Features

- Daily aggregation of nutrition data (multiple meals per day)
- Flexible column-name matching (works with different CSV schemas)
- Fiber-aware macro energy calculations (4–4–9 rule with net carbs)
- Correlation plots:
  - Calories vs carbohydrates, protein, fat
  - (Optional) nutrition metrics vs time at home
- Configurable nutrition scoring system
- Automatic plot and result generation
- Optional Snakemake integration for reproducible workflows

---

## Project Structure

```
Cern Project/
│
├── config.py
├── data_files_csv/
│   ├── Nutrition-Summary-*.csv
│   └── home_time.csv
│
├── scripts/
│   └── main.py
│
├── src/
│   ├── data_loader.py
│   ├── features.py
│   ├── scoring.py
│   └── plots.py
│
├── outputs/
├── Snakefile
└── README.md
```

---

## Requirements

- Python 3.9+
- pandas
- numpy
- matplotlib

Install dependencies:
```bash
pip install pandas numpy matplotlib
```

---

## Configuration

Edit `config.py` to:
- Set file paths
- Define column-name aliases
- Filter dates
- Adjust nutrition targets

---

## Running the Analysis

From the project root:
```bash
python scripts/main.py
```

Results are written to `results/`.

---

## Nutrition Scoring

Each day is scored from 0–100 based on target ranges for calories and macro percentages.
All metrics are equally weighted by default and easily adjustable.


---

## Notes

- Home-time analysis is skipped automatically if no home-time file is provided.
- The project is modular and easy to extend if You want to get some extra plots.

---

## Author
Algirdas Dienys, FF, Light engineering
