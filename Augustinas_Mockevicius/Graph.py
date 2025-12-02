import pandas as pd            # data manipulation, CSV loading, and table operations
import os                     # filesystem path handling and directory operations
import sys                    # access to Python executable/path and system args
import re                     # regular expressions for parsing and detection
import matplotlib.pyplot as plt  # plotting library for charts
import numpy as np            # numerical routines, arrays, and polynomial fits
from datetime import datetime # timestamp filenames and parse/format dates

#! Run this in terminal to open folder path (This is the file path, different for everyone):

# cd "c:\Users\augus\Desktop\Python\Augustinas_Mockevicius" 

#! To auto separate columns by commas use this code:

# python Seperate.py [File name here] --group-by-header --replace-literal-tabs --inplace

#! Run the graph builder script in terminal:

# python Graph.py



def parse_numeric_string(value):
    """
    Parse numeric strings with various formats into float.
    Supports: percentages ('95%'), thousands separators ('1,000.5'), scientific notation ('1e-5'), currency.
    Returns float if parseable, otherwise returns None.
    """
    if pd.isna(value):
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if not isinstance(value, str):
        return None
    
    # Normalize whitespace (including NBSP) and strip
    if isinstance(value, str):
        value = value.replace('\u00A0', ' ').strip()
    value = value.strip() if isinstance(value, str) else value
    
    if not value:
        return None
    
    # Common missing-value markers
    if isinstance(value, str) and value in ['-', '–', '—', 'na', 'n/a', '']:
        return None

    # Handle percentage (e.g., "95%", "95.5%")
    if value.endswith('%'):
        try:
            return float(value[:-1].strip()) / 100
        except ValueError:
            return None
    
    # Remove currency symbols ($, €, £, ¥, etc.)
    value = re.sub(r'[\$€£¥₹]', '', value)

    # Remove ANY alphabetic unit suffixes (kHz, MHz, GHz, dB, V, mV, kV, A, mA, W, kW, Hz, etc.)
    # This strips all letters/units from data rows, leaving only the header row with units intact
    if isinstance(value, str):
        # Match: optional sign, digits with optional decimal/comma, followed by ANY alphabetic suffix
        # This pattern captures numbers with ANY letter suffix and extracts just the number
        unit_pattern = r'^([+-]?\d[\d\.,]*)\s*[a-zA-Z°µ]+$'
        m = re.match(unit_pattern, value)
        if m:
            numeric_part = m.group(1)
            # Remove commas from numeric part
            value = numeric_part.replace(',', '')
        else:
            # No unit suffix found, proceed with original value
            pass

    # Convert common multiplication/scientific formats like '3.72*10^9' or '3.72×10^9' to '3.72e9'
    if isinstance(value, str):
        # remove spaces used as thousands separators
        value_no_space = value.replace(' ', '').replace('\u00A0', '')
        # pattern: xxx * 10^exp  (allow *, ×)
        m = re.match(r'^([+-]?\d[\d\.,]*)\s*(?:\*|×|x)\s*10\^?([+-]?\d+)$', value_no_space, flags=re.IGNORECASE)
        if m:
            mant = m.group(1).replace(',', '')
            exp = int(m.group(2))
            try:
                return float(mant) * (10 ** exp)
            except Exception:
                pass
        # Accepts '3.72E+09' or '3.72e9'

    # Remove commas, but keep decimal point
    if isinstance(value, str):
        value = value.replace(',', '')

    # parse as float (handles regular numbers and scientific notation like 1e-5)
    try:
        return float(value)
    except Exception:
        return None


def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    Auto-detects delimiter from common options: comma, semicolon, colon, tab, pipe.
    Uses the delimiter.
    FileNotFoundError if file doesn't exist, or ValueError if read/parse fails / file is empty.
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    # Try common delimiters
    delimiters = [',', ';', ':', '\t', '|']
    best_df = None
    best_delim = ','
    best_cols = 1
    
    for delim in delimiters:
        try:
            test_df = pd.read_csv(filepath, sep=delim)
            if len(test_df.columns) > best_cols:
                best_cols = len(test_df.columns)
                best_delim = delim
                best_df = test_df
        except Exception:
            continue
    
    # If no delimiter worked, try with ,
    if best_df is None:
        try:
            best_df = pd.read_csv(filepath, sep=',')
        except Exception as e:
            raise ValueError(f"Could not read CSV file with any common delimiter: {e}")
    
    df = best_df
    
    if df.empty:
        raise ValueError("CSV file is empty.")
    
    # Show what delimiter was detected
    delim_names = {',': 'comma', ';': 'semicolon', ':': 'colon', '\t': 'tab', '|': 'pipe'}
    delim_name = delim_names.get(best_delim, repr(best_delim))
    print("="*40 + f"\nAuto-detected delimiter: {delim_name}")
    print(f"Detected {len(df.columns)} columns and {len(df)} rows." + "\n" + "="*40)
    return df


# choosing the CSV file
def choose_csv_file(folder_path: str) -> str:
    """
    Interactive file picker: list all .csv files in folder and let user select by number.
    Returns full path to chosen file. User can enter 'cancel' or 'q' to exit.
    """
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Not a valid folder: {folder_path}")

    print(f"" + "="*50 + f"\nLooking for CSV files in: {folder_path}")

    # List all .csv files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError("No CSV files found in this folder.")

    print("\nCSV files found:")
    for i, fname in enumerate(csv_files):
        print(f"{i}: {fname}")

    while True:
        choice = input("\nNumber of file to use ('q' to Quit): ").strip().lower()

        if choice in ["cancel", "q", "quit"]:
            print("\nProcess cancelled. Exiting...")
            exit()

        try:
            idx = int(choice)
            if 0 <= idx < len(csv_files):
                chosen_file = csv_files[idx]
                break
            else:
                print(f"Enter a number between 0 and {len(csv_files) - 1}.")
        except ValueError:
            print("That is not a valid number. Try again.")

    full_path = os.path.join(folder_path, chosen_file)
    return full_path


def choose_axes(df: pd.DataFrame):
    """
    Prompt user to select X column (single) and Y column(s) (comma-separated, multiple allowed).
    Returns tuple: (x_col_name, [y_col_names]).
    """
    print("\n\nColumns Found:")
    for i, col in enumerate(df.columns):
        print(f"{i}: {col}")

    print("=" * 30)
    # User selects X axis column
    while True:
        x_choice = input("Enter the column number for the X axis: ").strip()
        try:
            x_idx = int(x_choice)
            if 0 <= x_idx < len(df.columns):
                x_col = df.columns[x_idx]
                break
            else:
                print(f"Enter a number between 0 and {len(df.columns) - 1}.")
        except ValueError:
            print("That is not a valid number. Try again.")

    # User selects Y axis column(s); comma-separated list for multiple columns
    while True:
        y_choice = input("Enter column number(s) for Y axis data: ").strip()
        try:
            indices = [int(x.strip()) for x in y_choice.split(",")]
            if not indices:
                print("You must choose at least one Y column.")
                continue

            invalid = [i for i in indices if i < 0 or i >= len(df.columns)]
            if invalid:
                print(f"Invalid indices: {invalid}. Try again.")
                continue

            # Remove duplicates, keep order
            y_indices = []
            for i in indices:
                if i not in y_indices:
                    y_indices.append(i)


            y_cols = [df.columns[i] for i in y_indices]
            break
        except ValueError:
            print("Could not get that. Use numbers separated by commas.") # Try again if miss clicked

    return x_col, y_cols


def show_summary_stats(df: pd.DataFrame, numeric_cols: list):
    """
    Display summary statistics (min, max, mean, median, std) for all columns.
    User chooses which statistics to display via comma-separated selection (e.g., 1,3,5).
    Optionally compute linear slope(s) (y = m*x + b) between a chosen X column and one or more Y columns.
    """
    print("\n" + "=" * 20)
    print("SUMMARY STATISTICS")
    print("1: Minimum")
    print("2: Maximum")
    print("3: Mean")
    print("4: Median")
    print("5: Standard deviation")
    print("6: All statistics")
    print("7: Compute slope(s) for chosen X and Y columns")
    print("\nEnter choice(s), comma-separated.")
    print("Or press Enter to skip statistics")
    print("=" * 20)
    choice = input("Enter your choice: ").strip()
    if choice == "":
        return

    stats_list = ["min", "max", "mean", "median", "std"]
    selected = []
    slope_requested = False

    # Parse comma-separated numbers
    try:
        indices = [int(x.strip()) for x in choice.split(",")]
    except ValueError:
        print("Invalid input. Could not parse numbers.")
        return

    if 6 in indices:
        selected = stats_list.copy()

    for idx in indices:
        if idx == 6:
            continue
        if idx == 7:
            slope_requested = True
            continue
        if 1 <= idx <= 5:
            stat_name = stats_list[idx - 1]
            if stat_name not in selected:
                selected.append(stat_name)
        else:
            print(f"Warning: {idx} is not a valid choice (1-7). Skipping.")

    if not selected and not slope_requested:
        print("No valid statistics selected.")
        return

    # Calculate requested statistics (min/max/mean/median/std) for each numeric column
    stats_results = {}
    for col in numeric_cols:
        try:
            # Convert to numeric using smart parsing (handles percentages, currency, etc.)
            data = df[col].apply(parse_numeric_string).dropna()
            if len(data) == 0:
                print(f"\n{col}: (no numeric data)")
                continue
            col_stats = {}
            if "min" in selected:
                col_stats['min'] = data.min()
            if "max" in selected:
                col_stats['max'] = data.max()
            if "mean" in selected:
                col_stats['mean'] = data.mean()
            if "median" in selected:
                col_stats['median'] = data.median()
            if "std" in selected:
                col_stats['std'] = data.std()

            # Print to console as before
            print(f"\n{col}:" + "\n" + "-" * 30)
            for k, v in col_stats.items():
                label = k.capitalize()
                print(f"  {label}: {v:.6g}")
            print("-"*30)
            stats_results[col] = col_stats
        except Exception as e:
            print(f"\n{col}: Could not compute statistics ({e})")

    # If slope computation requested, prompt for X and Y columns and compute
    if slope_requested:
        print("\nSLOPE COMPUTATION")
        print("Available columns:")
        for i, col in enumerate(df.columns):
            print(f"{i}: {col}")

        # Choose X axis
        while True:
            x_choice = input("\nEnter the column number to use as X for slope calculation ('c' to cancel): ").strip()
            if x_choice.lower() in ["c", "cancel"]:
                print("Slope computation cancelled.")
                return
            try:
                x_idx = int(x_choice)
                if 0 <= x_idx < len(df.columns):
                    x_col = df.columns[x_idx]
                    break
                else:
                    print(f"Enter a number between 0 and {len(df.columns) - 1}.")
            except ValueError:
                print("That is not a valid number. 'c' to cancel.")

        # Choose Y axes
        while True:
            y_choice = input("Enter column number(s) for Y. 'c' to cancel: ").strip()
            if y_choice.lower() in ["c", "cancel"]:
                print("Slope computation cancelled.")
                return
            try:
                y_indices = [int(x.strip()) for x in y_choice.split(",")]
                # Validate indices
                invalid = [i for i in y_indices if i < 0 or i >= len(df.columns)]
                if invalid:
                    print(f"Invalid indices: {invalid}. Try again.")
                    continue
                # Remove X if present in Y list
                y_indices = [i for i in y_indices if i != x_idx]
                if not y_indices:
                    print("Y columns cannot be the same as X. Choose different column(s).")
                    continue
                y_cols = [df.columns[i] for i in y_indices]
                break
            except ValueError:
                print("Could not parse that. Use numbers separated by commas.")

        # Compute linear slope (m) and intercept (b) for fitted line y = m*x + b, plus R² quality
        for ycol in y_cols:
            try:
                # Align X and Y: drop rows where either column has NaN or non-numeric value
                x_vals = df[x_col].apply(parse_numeric_string)
                y_vals = df[ycol].apply(parse_numeric_string)
                valid = pd.concat([x_vals, y_vals], axis=1).dropna()
                if valid.empty:
                    print(f"\n{ycol}: (no numeric data after alignment with X)")
                    continue
                x = valid[x_col].values
                y = valid[ycol].values
                # Fit linear polynomial: np.polyfit returns [slope, intercept] for degree=1
                slope, intercept = np.polyfit(x, y, 1)
                # Compute R² (coefficient of determination): 0=poor fit, 1=perfect fit
                y_pred = slope * x + intercept  # Predicted y values from fitted line
                ss_res = ((y - y_pred) ** 2).sum()  # Sum of squared residuals (prediction errors)
                ss_tot = ((y - y.mean()) ** 2).sum()  # Total sum of squares (data variance)
                r2 = 1.0 - ss_res / ss_tot if ss_tot != 0 else float('nan')  # R² = 1 - (residual/total)
                print(f"\n{ycol} vs {x_col}:")
                print(f"  Slope:     {slope:.6g}")
                print(f"  Intercept: {intercept:.6g}")
                if not (r2 != r2):  # check for NaN
                    print(f"  R^2:       {r2:.6g}")
            except Exception as e:
                print(f"\n{ycol}: Could not compute slope ({e})")

    # Return selected stat keys and numeric results so the caller can annotate plots
    return selected, stats_results


def pick_row_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Selecting range to use for analysis/plotting.
    """
    total = len(df)
    if total == 0:
        print("No rows available in the dataset.")
        return df
    print("=" * 50)
    print(f"Rows available: 1 - {total}")
    choice = input("Would you like to graph a part of rows? (Y/N): ").strip().upper()
    if choice != "Y":
        return df

    while True:
        start_str = input("Enter start row number: ").strip() # row start
        end_str = input("Enter end row number: ").strip() # row end
        try:
            start = int(start_str)
            end = int(end_str)
        except ValueError:
            print("Invalid input. Enter integer row numbers.") # if not integer
            continue

        if start < 1 or end < 1 or start > end or end > total: # checks if range is valid
            print(f"Invalid range. Please enter values between 1 and {total}, and start <= end.")
            continue

        # Slice using iloc (end is inclusive for users, iloc end is exclusive)
        sliced = df.iloc[start - 1:end].reset_index(drop=True) # reset_index to renumber rows
        print(f"Selected rows: {start} to {end} ({len(sliced)} rows)")
        return sliced


def filter_data(df: pd.DataFrame, x_col: str, y_cols: list) -> pd.DataFrame:
    """
    Filter data rows by a user-specified condition (e.g., column > value).
    Returns filtered DataFrame; if no filter chosen, returns full DataFrame unchanged.
    """
    print("=" * 50)
    filter_choice = input("Filter Points of Interest? (Y/N): ").strip().upper()
    if filter_choice != "Y":
        return df
    
    all_cols = [x_col] + y_cols
    print("\nAvailable columns:")
    for i, col in enumerate(all_cols):
        print(f"{i}: {col}")
    
    col_idx = input("\nEnter column number to filter on: ").strip()
    try:
        col_idx = int(col_idx)
        if col_idx < 0 or col_idx >= len(all_cols):
            print("Invalid column index.")
            return df
        filter_col = all_cols[col_idx]
    except ValueError:
        print("Invalid input.")
        return df
    print("\n" + "=" * 30)
    print("\nFilter operators:")
    print("1: > (greater than)")
    print("2: < (less than)")
    print("3: >= (greater or equal)")
    print("4: <= (less or equal)")
    print("5: == (equal to)")
    print("6: != (not equal to)")
    print("7: Between (Value range)")
    print("\n" + "=" * 30)
    
    op_choice = input("Enter operator (1-7): ").strip()
    op_map = {"1": ">", "2": "<", "3": ">=", "4": "<=", "5": "==", "6": "!=", "7": "between"}
    op = op_map.get(op_choice)
    if not op:
        print("Invalid operator.")
        return df
    
    # Prepare numeric column for comparison
    col_data = df[filter_col].apply(parse_numeric_string)

    # Handle 'between' operator specially (two inputs)
    if op == "between":
        print("\nBetween operator: include bounds or exclude?")
        print("1: Exclusive (> low AND < high)")
        print("2: Inclusive (>= low AND <= high)")
        inclusive_choice = input("Enter choice (1-2): ").strip() or "1"
        inclusive = (inclusive_choice == "2")
        
        low_str = input(f"Enter lower bound for {filter_col}: ").strip()
        high_str = input(f"Enter upper bound for {filter_col}: ").strip()
        try:
            low = float(low_str)
            high = float(high_str)
        except ValueError:
            print("Invalid bound values.")
            return df
        
        if inclusive:
            mask = (col_data >= low) & (col_data <= high)
            bound_desc = f"between {low} and {high} (inclusive)"
        else:
            mask = (col_data > low) & (col_data < high)
            bound_desc = f"between {low} and {high} (exclusive)"
    else:
        value_str = input(f"Enter value to compare {filter_col} {op} : ").strip()
        try:
            value = float(value_str)
        except ValueError:
            print("Invalid value.")
            return df
        # Apply the chosen comparison operator to create a boolean mask (True = rows to keep)
        if op == ">":
            mask = col_data > value
        elif op == "<":
            mask = col_data < value
        elif op == ">=":
            mask = col_data >= value
        elif op == "<=":
            mask = col_data <= value
        elif op == "==":
            mask = col_data == value
        elif op == "!=":
            mask = col_data != value
    
    # Filter DataFrame using mask; reset_index renumbers rows starting at 0
    filtered_df = df[mask].reset_index(drop=True)
    # Print an informative message depending on operator used
    if op == "between":
        print(f"\nFiltered: {len(filtered_df)} of {len(df)} rows match {filter_col} {bound_desc}")
    else:
        print(f"\nFiltered: {len(filtered_df)} of {len(df)} rows match {filter_col} {op} {value}")
    return filtered_df


def sample_data_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sample data by plotting every Nth point (useful for large datasets).
    Returns sampled DataFrame or full DataFrame if sampling skipped.
    """
    total = len(df)
    if total == 0:
        return df
    
    print("\n" + "=" * 50)
    print("DATA POINT SAMPLING (for large datasets)")
    print("=" * 50)
    print(f"Total data points: {total}")
    
    # Only prompt if dataset is reasonably large
    if total < 100:
        print("Dataset is small enough to plot all points.")
        return df
    
    choice = input("\nPlot every Nth point to reduce density? (Y/N): ").strip().upper()
    if choice != "Y":
        return df
    
    while True:
        step_str = input(f"Enter step size: ").strip()
        try:
            step = int(step_str)
            if step < 1:
                print("Step must be at least 1.")
                continue
            if step >= total:
                print(f"Step too large. Must be less than {total}.")
                continue
            break
        except ValueError:
            print("Invalid input. Enter an integer.")
    
    # Sample every Nth row using iloc with step
    sampled = df.iloc[::step].reset_index(drop=True)
    print(f"Sampled {len(sampled)} points (every {step} point(s)) from {total} total.")
    return sampled


def plot_data(df: pd.DataFrame, x_col: str, y_cols: list):
    """
    Plot selected X and Y columns with multiple plot types (line/scatter/bar/histogram).
    Supports trend lines (linear/polynomial), dual Y-axis, and plot saving (PNG/PDF).
    """
    print("=" * 30 + "\n" + f"Plotting X: {x_col}")
    print(f"Plotting Y columns: {', '.join(y_cols)}" + "\n" + "=" * 30)

    # User chooses plot visualization type
    print("Plot types:")
    print("1: Line plot")
    print("2: Scatter plot")
    print("3: Bar chart")
    print("4: Histogram")
    
    plot_choice = input("\nEnter plot type (1-4): ").strip() or "1"
    plot_type = {"1": "line", "2": "scatter", "3": "bar", "4": "histogram"}.get(plot_choice, "line")

    # Ask about axis scaling (logarithmic, semi-log, etc.)
    print("\nAxis scaling:")
    print("1: Linear (default)")
    print("2: Log-log (both axes logarithmic)")
    print("3: Semi-log X (X logarithmic, Y linear)")
    print("4: Semi-log Y (X linear, Y logarithmic)")
    scale_choice = input("Enter scale type (1-4): ").strip() or "1"
    scale_type = {"1": "linear", "2": "loglog", "3": "semilogx", "4": "semilogy"}.get(scale_choice, "linear")

    # Ask about trend line (for line/scatter only)
    # Trend line choice: 0=None, 1=Linear, 2=Polynomial (keeps logic consistent below)
    trend_choice = None
    if plot_type in ["line", "scatter"]:
        trend_choice = input("Add trend line? (0=None, 1=Linear, 2=Polynomial): ").strip() or "0"
    
    # Ask about dual Y-axis (for line/scatter plots with multiple series)
    dual_axis = False
    right_axis_cols = []  # Y columns assigned to right axis
    y_axis_ranges = {}  # store min/max for each Y column
    if len(y_cols) > 1 and plot_type in ["line", "scatter"]:
        dual_choice = input("Use dual Y-axis for different scales? (Y/N): ").strip().upper()
        dual_axis = (dual_choice == "Y")
        
        # If dual axis enabled, let user choose which columns go on right axis
        if dual_axis:
            print("\nSelect which Y columns go on the RIGHT axis:")
            print("Available Y columns:")
            for idx, y_col in enumerate(y_cols):
                print(f"{idx}: {y_col}")
            
            right_choice = input("\nEnter column numbers for RIGHT axis (comma-separated, or leave blank for default split): ").strip()
            if right_choice:
                try:
                    right_indices = [int(x.strip()) for x in right_choice.split(",")]
                    right_axis_cols = [y_cols[i] for i in right_indices if 0 <= i < len(y_cols)]
                    if not right_axis_cols:
                        print("  No valid right-axis columns, using default: first on left, rest on right")
                        right_axis_cols = y_cols[1:]
                except Exception:
                    print("  Invalid input, using default: first on left, rest on right")
                    right_axis_cols = y_cols[1:]
            else:
                # Default: first column on left, rest on right
                right_axis_cols = y_cols[1:]
            
            print(f"\nLeft axis: {[c for c in y_cols if c not in right_axis_cols]}")
            print(f"Right axis: {right_axis_cols}")
            
            # Allow user to set custom ranges for each axis
            print("\nSet Y-axis ranges:")
            for idx, y_col in enumerate(y_cols):
                side = "RIGHT" if y_col in right_axis_cols else "LEFT"
                print(f"\n{y_col} ({side} axis):")
                y_min_str = input(f"  Min value (blank for auto): ").strip()
                y_max_str = input(f"  Max value (blank for auto): ").strip()
                
                y_min = None
                y_max = None
                try:
                    if y_min_str:
                        y_min = float(y_min_str)
                    if y_max_str:
                        y_max = float(y_max_str)
                except ValueError:
                    print(f"  Warning: Invalid range values, using auto-fit")
                
                y_axis_ranges[y_col] = (y_min, y_max)
    
    # Ask about legend customization
    print("=" * 50)
    print("Legend:")
    print("1: Default - upper left")
    print("2: Custom position / label")
    print("3: Custom labels")
    print("4: Hide legend")
    legend_choice = input("Enter choice (1-4): ").strip() or "1"
    
    # Ask for custom chart title
    custom_title = input("\nEnter custom chart title: ").strip()
    if not custom_title:
        custom_title = "Laboratory Data Analysis"
    
    # Handle custom legend labels
    custom_labels = {}
    if legend_choice == "3":
        print("\nEnter custom labels for each Y column (blank for original):")
        for y_col in y_cols:
            label = input(f"Label for '{y_col}': ").strip()
            if label:
                custom_labels[y_col] = label
            else:
                custom_labels[y_col] = y_col
    else:
        custom_labels = {y_col: y_col for y_col in y_cols}
    
    # Determine legend position (for later use)
    legend_pos = "upper left"  # default
    if legend_choice == "2":  # Custom position
        positions = {
            "1": "upper left", "2": "upper center", "3": "upper right",
            "4": "center left", "5": "center", "6": "center right",
            "7": "lower left", "8": "lower center", "9": "lower right",
            "0": "upper left"
        }
        print("\nLegend positions:")
        for k, v in positions.items():
            print(f"{k}: {v}")
        pos_choice = input("Enter position (0-9): ").strip() or "0"
        legend_pos = positions.get(pos_choice, "upper left")
    
    # Convert X column to numeric using smart parsing; if X has no numeric values, treat as categorical
    try:
        x_parsed = df[x_col].apply(parse_numeric_string)
    except Exception as e:
        raise ValueError(f"Could not convert X column to numeric: {e}")

    categorical_x = False
    x_labels = None
    if x_parsed.dropna().empty:
        # No numeric X values -> categorical axis (use string labels)
        categorical_x = True
        x_labels = df[x_col].astype(str).tolist()
        x = pd.Series(range(len(x_labels)))
    else:
        x = x_parsed

    # Create figure with main axis
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = None
    
    # Color palette for each Y series
    colors = plt.cm.tab10(np.linspace(0, 1, len(y_cols)))

    # Plot each Y column
    for idx, y_col in enumerate(y_cols):
        try:
            # Convert Y to numeric using smart parsing; drop NaN values
            y = df[y_col].apply(parse_numeric_string)
        except Exception as e:
            print(f"Skipping column {y_col}: could not convert to numeric. Error: {e}")
            continue
        
        # Select axis: use ax2 (right) for columns in right_axis_cols, otherwise use ax1 (left)
        current_ax = ax1
        if dual_axis and y_col in right_axis_cols:
            if ax2 is None:
                ax2 = ax1.twinx()  # Create second Y-axis sharing same X-axis
            current_ax = ax2

        # Plot based on type
        if plot_type == "line":
            # Line plot
            current_ax.plot(x, y, marker="o", markersize=6, linestyle="-", linewidth=2.5, 
                           label=custom_labels[y_col], color=colors[idx])
            
            # Add trend line
            if trend_choice == "1":
                # Linear trend: align numeric x and y values and fit slope/intercept
                valid_xy = pd.concat([x, y], axis=1).apply(pd.to_numeric, errors="coerce").dropna()
                if len(valid_xy) > 1:
                    xv = valid_xy.iloc[:, 0].values
                    yv = valid_xy.iloc[:, 1].values
                    slope, intercept = np.polyfit(xv, yv, 1)
                    p = np.poly1d([slope, intercept])
                    x_trend = np.linspace(xv.min(), xv.max(), 100)
                    current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8,
                                   color=colors[idx], label=f"{y_col} trend")
                    txt = f"Slope: {slope:.3g}\nIntercept: {intercept:.3g}"
                    y_offset = 0.95 - (idx * 0.08)
                    current_ax.text(0.02, y_offset, txt, transform=current_ax.transAxes,
                                    color=colors[idx], fontsize=10, fontweight='bold',
                                    bbox=dict(facecolor='white', alpha=0.75, edgecolor=colors[idx], linewidth=1.5))
            elif trend_choice == "2":
                # Polynomial (degree 2) trend: align and fit using numeric X values
                valid_xy = pd.concat([x, y], axis=1).apply(pd.to_numeric, errors="coerce").dropna()
                if len(valid_xy) > 2:
                    xv = valid_xy.iloc[:, 0].values
                    yv = valid_xy.iloc[:, 1].values
                    z = np.polyfit(xv, yv, 2)
                    p = np.poly1d(z)
                    x_trend = np.linspace(xv.min(), xv.max(), 100)
                    current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8,
                                   color=colors[idx], label=f"{y_col} poly fit")
                
        elif plot_type == "scatter":
            # Scatter plot
            current_ax.scatter(x, y, s=80, marker='x', color=colors[idx], label=custom_labels[y_col], alpha=1.0, linewidths=2)
            
            if trend_choice == "1":
                # Linear trend for scatter: align numeric x and y values and fit
                valid_xy = pd.concat([x, y], axis=1).apply(pd.to_numeric, errors="coerce").dropna()
                if len(valid_xy) > 1:
                    xv = valid_xy.iloc[:, 0].values
                    yv = valid_xy.iloc[:, 1].values
                    slope, intercept = np.polyfit(xv, yv, 1)
                    p = np.poly1d([slope, intercept])
                    x_trend = np.linspace(xv.min(), xv.max(), 100)
                    current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8,
                                   color=colors[idx], label=f"{y_col} trend")
                    txt = f"Slope: {slope:.3g}\nIntercept: {intercept:.3g}"
                    y_offset = 0.95 - (idx * 0.08)
                    current_ax.text(0.02, y_offset, txt, transform=current_ax.transAxes,
                                    color=colors[idx], fontsize=10, fontweight='bold',
                                    bbox=dict(facecolor='white', alpha=0.75, edgecolor=colors[idx], linewidth=1.5))
            elif trend_choice == "2":
                # Polynomial (degree 2) fit for scatter: use numeric X values
                valid_xy = pd.concat([x, y], axis=1).apply(pd.to_numeric, errors="coerce").dropna()
                if len(valid_xy) > 2:
                    xv = valid_xy.iloc[:, 0].values
                    yv = valid_xy.iloc[:, 1].values
                    z = np.polyfit(xv, yv, 2)
                    p = np.poly1d(z)
                    x_trend = np.linspace(xv.min(), xv.max(), 100)
                    current_ax.plot(x_trend, p(x_trend), "--", linewidth=2, alpha=0.8,
                                   color=colors[idx], label=f"{y_col} poly fit")
                
        elif plot_type == "bar":
            # Bar chart: support categorical X and numeric X, with value annotations
            # Ensure Y is numeric
            y_vals = pd.to_numeric(y, errors='coerce')
            n = len(y_vals)
            if categorical_x:
                # Grouped bars: offset each series horizontally
                base_pos = np.arange(n)
                num_series = len(y_cols)
                width = 0.8 / max(1, num_series)
                # compute positions for this series
                pos = base_pos - 0.4 + idx * width + width / 2
                bars = current_ax.bar(pos, y_vals, width=width, label=custom_labels[y_col], alpha=0.85, color=colors[idx], edgecolor='black', linewidth=1.0)
                # set xticks on main axis (ax1)
                if current_ax is ax1:
                    ax1.set_xticks(base_pos)
                    ax1.set_xticklabels(x_labels, rotation=45, ha='right')
                # annotate values above bars
                for rect, val in zip(bars, y_vals):
                    if not np.isnan(val):
                        current_ax.text(rect.get_x() + rect.get_width()/2, rect.get_height(), f"{val:.3g}",
                                        ha='center', va='bottom', fontsize=9, color='black')
            else:
                # Numeric X: plot using X values directly
                bars = current_ax.bar(x, y_vals, label=custom_labels[y_col], alpha=0.75, color=colors[idx], edgecolor='black', linewidth=1.2)
                current_ax.set_xticks(x)
                # annotate values above bars
                for rect, val in zip(bars, y_vals):
                    if not np.isnan(val):
                        current_ax.text(rect.get_x() + rect.get_width()/2, rect.get_height(), f"{val:.3g}",
                                        ha='center', va='bottom', fontsize=9, color='black')
            
        elif plot_type == "histogram":
            # Histogram: distribution of Y values (bins=20 intervals) with edge color
            current_ax.hist(y.dropna(), bins=20, label=custom_labels[y_col], alpha=0.7, color=colors[idx], edgecolor='black', linewidth=1)

    # Set axis labels and title with larger, bold fonts
    ax1.set_xlabel(x_col, fontsize=12, fontweight='bold')
    if not dual_axis:
        # Single Y-axis: label lists all Y columns
        ax1.set_ylabel(", ".join(y_cols), fontsize=12, fontweight='bold')
    else:
        # Dual Y-axis: left axis shows columns NOT in right_axis_cols, right axis shows right_axis_cols
        left_cols = [c for c in y_cols if c not in right_axis_cols]
        left_label = ", ".join(left_cols) if left_cols else ""
        right_label = ", ".join(right_axis_cols) if right_axis_cols else ""
        
        if left_label:
            # Use neutral color for left axis label to avoid confusion
            ax1.set_ylabel(left_label, fontsize=12, fontweight='bold', color='black')
            ax1.tick_params(axis='y', labelcolor='black', labelsize=10)
        
        if ax2 and right_label:
            # Use neutral color for right axis label to avoid confusion
            ax2.set_ylabel(right_label, fontsize=12, fontweight='bold', color='black')
            ax2.tick_params(axis='y', labelcolor='black', labelsize=10)
        
        # Apply custom Y-axis ranges if specified (for all left/right columns)
        for y_col in left_cols:
            if y_col in y_axis_ranges:
                y_min, y_max = y_axis_ranges[y_col]
                if y_min is not None or y_max is not None:
                    ax1.set_ylim(y_min, y_max)
                    break  # Apply first valid range to left axis
        
        if ax2:
            for y_col in right_axis_cols:
                if y_col in y_axis_ranges:
                    y_min, y_max = y_axis_ranges[y_col]
                    if y_min is not None or y_max is not None:
                        ax2.set_ylim(y_min, y_max)
                        break  # Apply first valid range to right axis
    
    # If X is categorical, apply labels for all plot types
    if 'categorical_x' in locals() and categorical_x and x_labels:
        ax1.set_xticks(np.arange(len(x_labels)))
        ax1.set_xticklabels(x_labels, rotation=45, ha='right')

    # Apply axis scaling (logarithmic, semi-log, etc.)
    if scale_type == "loglog":
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        if ax2:
            ax2.set_yscale('log')
    elif scale_type == "semilogx":
        ax1.set_xscale('log')
    elif scale_type == "semilogy":
        ax1.set_yscale('log')
        if ax2:
            ax2.set_yscale('log')

    # Improve title and styling
    ax1.set_title(custom_title, fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.4, linestyle='--', linewidth=0.7)  # Enhanced grid: dashed lines, better visibility
    ax1.tick_params(axis='x', labelsize=10)
    
    # Enhanced legend with better positioning and frame
    if legend_choice != "4":  # "4" means hide legend
        legend1 = ax1.legend(loc=legend_pos, fontsize=10, framealpha=0.95, edgecolor='black', fancybox=True, shadow=True)
        if ax2:
            ax2.legend(loc='upper right', fontsize=10, framealpha=0.95, edgecolor='black', fancybox=True, shadow=True)
    
    # Add light background color for readability
    ax1.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    plt.tight_layout()  # Auto-adjust spacing to avoid label cutoff
    
    # User chooses whether to save plot to disk
    print("=" * 37)
    save_choice = input("Save plot? (0=none, 1=PNG, 2=PDF): ").strip() or "1" # default - no save
    print("=" * 15 + " Enjoy " + "=" * 15)
    if save_choice in ["1", "2"]: # if user chose to save
        script_dir = os.path.dirname(os.path.abspath(__file__)) # script directory
        # Create "Saved Graphs" folder if it doesn't exist
        saved_graphs_dir = os.path.join(script_dir, "Saved Graphs")
        os.makedirs(saved_graphs_dir, exist_ok=True)
        
        ext = ".png" if save_choice == "1" else ".pdf" # determine file extension
        
        # Determine prefix based on plot type
        prefix_map = {"line": "Lin.", "scatter": "Sc.", "bar": "Bar.", "histogram": "Hist."}
        prefix = prefix_map.get(plot_type, "")
        
        # Ask user for custom filename (default: use chart title)
        default_name = custom_title.replace(" ", ".").replace("/", "-").replace("\\", "-")
        user_filename = input(f"\nEnter filename (blank for '{default_name}'): ").strip()
        if not user_filename:
            user_filename = default_name
        
        # Remove extension if user added it (we'll add the correct one)
        user_filename = user_filename.replace(".png", "").replace(".pdf", "")
        
        # Generate final filename with prefix and timestamp to avoid overwriting
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(saved_graphs_dir, f"{prefix}{user_filename}_{timestamp}{ext}")
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')  # Higher DPI for quality
        print(f"Plot saved to: {filename}") # inform user of saved file
    
    plt.show()  # Display plot in window


def main():
    """
    Main workflow: load CSV, compute statistics, filter data, and generate plots.
    """
    # Folder where this script lives
    script_dir = os.path.dirname(os.path.abspath(__file__))
    separated_dir = os.path.join(script_dir, "Seperated")
    
    # If Seperated folder exists and has CSV files, use it as default; otherwise use script directory
    if os.path.isdir(separated_dir) and any(f.lower().endswith('.csv') for f in os.listdir(separated_dir)):
        default_dir = separated_dir
        print("\n"*8 + "=" * 120)
        print(f"Default folder: {separated_dir}")
        print("=" * 120)
    else:
        default_dir = script_dir
        print("\n"*8 + "=" * 120)
        print(f"Default folder: {script_dir}")
        print("=" * 120)
    folder_path = input(
        "\n=============> Graphinator 3000 <=============" + "\nEnter folder path containing your CSV files\n"
        f"(leave empty to use the default folder above): "
    ).strip()
    if folder_path == "":
        folder_path = default_dir

    # Store last settings for re-run functionality
    last_settings = None

    while True:
        while True:
            try:
                filepath = choose_csv_file(folder_path)
            except Exception as e:
                print(f"\nError selecting file: {e}")
                return

            # Try to load the CSV; if it fails, check heuristics and offer to run fix_csv.py
            loaded = False
            try:
                df = load_csv(filepath)
                loaded = True
            except Exception as e:
                print(f"\nInitial load failed: {e}")

            if not loaded:
                print("\nCould not load the selected CSV file. It may be corrupted or use non-standard separators.")
                print("If your file requires preprocessing (e.g. separating columns), run your fixer tool manually and try again.")

            if not loaded:
                retry = input("Choose a different file? (Y to choose again, any other key to exit): ").strip().upper()
                if retry == "Y":
                    print("Let's choose a different file.\n")
                    continue
                else:
                    return

            # If we reach here, df is loaded
            print(f"\nFile selected: {filepath}")
            print("\n" + "=" * 80)
            print(df.head())
            print("=" * 80)
            break

        # Show summary statistics
        # Identify columns that can be parsed as numeric (not just pure numeric types)
        numeric_cols = []
        for col in df.columns:
            # Check if at least one value in the column can be parsed as numeric
            if df[col].apply(parse_numeric_string).notna().any():
                numeric_cols.append(col)
        
        if numeric_cols:
            show_summary_stats(df, numeric_cols)
        
        # Choose axes and plot
        x_col, y_cols = choose_axes(df)

        # Optionally select a contiguous row range to analyze
        df = pick_row_range(df)

        # Filter data by points of interest
        df_filtered = filter_data(df, x_col, y_cols)

        # Sample data points (plot every Nth point for large datasets)
        df_sampled = sample_data_points(df_filtered)

        # Plot the data
        plot_data(df_sampled, x_col, y_cols)

        # Store settings for re-run
        last_settings = {
            'filepath': filepath,
            'x_col': x_col,
            'y_cols': y_cols
        }

        print("\n" + "=" * 50)
        print("1: Create new plot (different data/axes)")
        print("2: Re-run last plot with same settings")
        print("3: Exit")
        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "2" and last_settings:
            print("\nRe-running with last settings")
            filepath = last_settings['filepath']
            x_col = last_settings['x_col']
            y_cols = last_settings['y_cols']
            try:
                df = load_csv(filepath)
                df = pick_row_range(df)
                df_filtered = filter_data(df, x_col, y_cols)
                df_sampled = sample_data_points(df_filtered)
                plot_data(df_sampled, x_col, y_cols)
            except Exception as e:
                print(f"Error in re-run: {e}")
        elif choice == "1":
            print("\nStarting new plot session...\n")
            continue
        else:
            print("\nDone.")
            break


if __name__ == "__main__":
    main()
