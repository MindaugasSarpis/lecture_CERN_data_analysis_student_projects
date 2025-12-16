# CSV file cleaner/plotter tool

A command-line application for cleaning, transforming, plotting and exporting data from CSV files.

## Features

### Data Cleaning
- Remove rows/columns based on missing percentage
- Strip white space from column names and cells
- Normalize missing values
- Fix devimal commas
- Extract numeric values and units 
- Convert units to SI
- Remove duplicate rows
- Move rows/columns

### Simple plotting
- Choose x columns and Y column(s)
- Line, Scatter, Bar plots
- Linear/log axis scaling
- Grid
- Custom axis labels and titles
- Saves images as .png in the working folder

### LaTeX Export
- Outputs a standalone LaTeX document (.tex) ready to compile

## Requirements 
- Python 3
- pandas
- numpy
- matplotlib
- csv_actions.py and main.py should be in the same folder

## Works by running main.py

