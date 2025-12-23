# F1 Driver Season Analyzer (2020–2025)

A Python command-line application for analyzing Formula 1 driver performance using race result CSV data.

The program allows you to:
- Select an F1 season
- View the season champion
- Analyze individual driver performance
- Visualize results with graphs

---

##  Features

- Finishing position per race (visualized with colored markers)
- Points per race (bar chart with values)
- Cumulative points progression
- Driver summary (wins, podiums, DNFs, averages)
- Detailed result for a specific race

## Requirements
- Python 3.10+
- pandas
- matplotlib

## Setup

Create and activate a virtual environment(write in terminal one at a time):

python3 -m venv .venv
source .venv/bin/activate

Then to run the code type:
python3 f1_analyzer.py