================================================================================
                          GRAPHINATOR 3000 - README
================================================================================

WHAT IT DOES:
-------------
Graphinator is a tool that analyzes and visualizes CSV data.
Creating graphs from your Very sciency data with minimal effort.


HOW TO RUN:
-----------
1. Open terminal in the project folder and insert folder containing script data:
   cd "[Your file directions]"

2. Run the script:
   python Graphinator.py

3. Follow the on-screen prompts to select your data and create graphs


FEATURES:
---------
• Auto-detects CSV delimiters (comma, semicolon, tab, colon, pipe)
• Handles various number formats (percentages, currency, scientific notation)
• Statistical analysis (min, max, mean, median, std deviation, slope/R² calculation for selected X-Y)
• Multiple plot types:
  - Line plots with trend lines, text
  - Scatter plots
  - Bar charts with text labels
  - Histograms

• More advanced options:
  - Selection of CSV file in terminal
  - Dual Y-axis for different scales
  - Filter data by conditions (>, <, between, etc.)
  - Select specific row ranges (From 500 to 1000, etc.)
  - Sample large datasets (plot every N-th point)
  - Custom titles and legend positions
  - Categorical data support (text on X-axis, bar chart only)

• Save graphs as PNG or PDF to "Saved Graphs" folder


WORKFLOW:
---------
1. select file directions
2. Select CSV file
3. (Optional) View statistics, Slope
4. Choose X and Y (can be multiple) columns
5. (Optional) Pick row range
6. (Optional) Filter data
7. (Optional) Sample points for large datasets
8. Select plot type
9. (Optional) Linear/Polynomial trend line
10. Dual Y-axis selection
11. Min - Max values for each data column
12. Legend positioning, Custom chart title
13. Save or view graph
14. Create another plot or exit


TIPS:
-----
• Place preprocessed CSV files in the "Seperated" folder for quick access
• Use CommaInator.py to fix CSV formatting issues before graphing if needed
• For large datasets (>100 points), use sampling to improve density of data
• Press Enter to use default options for faster workflow

================================================================================
