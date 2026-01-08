# CSV_Visualizer

CSV_Visualizer is a Python tool designed to read CSV files, generate plots, and produce LaTeX tables for selected data. It is fully configurable via a command-line interface (CLI), allowing users to customize plotting options, and table formatting.

## Features

- Reads CSV files
- Plots columns against each other, with multiple Y columns supported
- Generates LaTeX tables with selectable columns, row frequency, and row range
- Supports custom plot labels, figure sizes, axis ranges, and engineering notation
- Fully configurable through CLI

## Requirements

- Python 3.8+  
- Packages:
  - matplotlib

## Installation

1. Download CSV_Visualizer.py and place it in your working directory
2. Install the required package using pip:

    -pip install matplotlib

## Usage

Run the program via command line:

python CSV_Visualizer.py --name <filename> [options]

### Example 1: Basic Plot and LaTeX table

python CSV_Visualizer.py --name figb20hz --inputpath "C:/Users/PC/Documents/lab works/applied electronics/1A/" --colx 1 --coly 2 3 --frequency 50 --ignorelines 7

- Plots column 1 vs columns 2 and 3
- Generates a LaTeX table with every 50th row
- Uses default settings for figure size, labels, and notation

### Example 2: Plot only

python CSV_Visualizer.py --name figb20hz --inputpath "C:/Users/PC/Documents/lab works/applied electronics/1A/" --colx 1 --coly 2 3 --maketable 0 --ignorelines 7

### Example 3: Custom axis labels and figure size

python CSV_Visualizer.py --name figb20hz --colx 1 --coly 2 3 --figuresize 12 8 --customxlabel 1 --xlabel "Time (ms)" --customylabel 1 --ylabel "Voltage (V)" --ignorelines 7

## CLI Arguments

File Input Options

| Argument | Description | Default | Required |
|----------|-------------|---------|---------|
| --name | Name of CSV file (without extension) | N/A | Yes |
| --inputpath | Path to CSV file | Current directory | No |
| --extension | Input file extension | .csv | No |
| --separator | CSV separator character | , | No |
| --ignorelines | Number of lines to skip at the start | 0 | No |
| --importlegend | Import header/legend from CSV (1=True, 0=False) | 1 | No |

Plot Options

| Argument | Description | Default |
|----------|-------------|---------|
| --plot | Generate plot (1=True, 0=False) | 1 |
| --colx | Column index for X axis | 0 |
| --coly | Column index(es) for Y axis | 1 |
| --figuresize | Plot figure size in inches (width height) | 8 6 |
| --customxlabel | Use custom X axis label (1=True, 0=False) | 0 |
| --xlabel | Custom X axis label (if enabled) | "x" |
| --customylabel | Use custom Y axis label (1=True, 0=False) | 0 |
| --ylabel | Custom Y axis label (if enabled) | "y(x)" |
| --customxrange | X axis range (start stop) | None |
| --customyrange | Y axis range (start stop) | None |
| --engnotation | Use engineering notation (1=True, 0=False) | 1 |

LaTeX Table Options

| Argument | Description | Default |
|----------|-------------|---------|
| --maketable | Generate LaTeX table (1=True, 0=False) | 1 |
| --columns | Columns to include in table | 0 1 2 3 |
| --frequency | Include every nth row | 1 |
| --range | Row range to include (start stop) | Full dataset |
| --samplecolumn | Convert first column to int (1=True, 0=False) | 0 |

## Notes / Limitations

- Zero-indexed columns: Column numbering starts from 0
- Windows paths: Use forward slashes (/) or double backslashes (\\) in paths to avoid escape issues.
- File reading: File must exist at the specified path; otherwise, the program will raise an error
- File must contain more than one column.
- File can contain only numeric data, other than metadata which can be ignored using CLI argument --ignorelines, if the metadata is located at the start of the file.

## Example Workflow

1. Prepare CSV file figb20hz.csv with numeric data
2. Run:

python CSV_Visualizer.py --name figb20hz --inputpath "C:/Users/PC/Documents/lab works/applied electronics/1A" --colx 1 --coly 2 3 --frequency 50

3. The program will generate:  
   - figb20hz.pdf containing the plot  
   - LaTeX table printed to the console, ready to copy into a .tex file

## Appended files

- figb20hz.csv (CSV file containing data to be visualized)
- figb20hz.pdf (Example plot)
- Table.txt (Example of generated table in LaTeX notation)
- Table.png (Image visualizing Table.txt)
