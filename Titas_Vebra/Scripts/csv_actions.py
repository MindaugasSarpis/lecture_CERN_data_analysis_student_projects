import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re

def remove_rows_and_columns(df: pd.DataFrame) -> pd.DataFrame:

    # print('Removing completely empty rows and columns...')
    # Work on a copy so you don't mutate original by accident
    df_clean = df.copy()
    df_clean = df_clean.replace(r'^\s*$', np.nan, regex=True)

    # what to remove
    while True:
        choice = input("Remove (r)ows, (c)olumns, or (b)oth? [r/c/b]: ").strip().lower()
        if choice in ("r", "c", "b"):
            break
        print("Please enter r, c, or b.")

    # threshold
    while True:
        try:
            p = float(input("Enter MAX allowed % of missing values (0–100): "))
            if 0 <= p <= 100:
                break
            else:
                print("Enter a number from 0 to 100.")
        except ValueError:
            print("Invalid number.")

    threshold = p / 100.0

    # compute on ORIGINAL df_clean (before any dropping)
    row_missing_fraction = df_clean.isna().mean(axis=1)
    col_missing_fraction = df_clean.isna().mean(axis=0)

    rows_ok = row_missing_fraction <= threshold
    cols_ok = col_missing_fraction <= threshold

    if choice == "r":
        # only rows filtered
        return df_clean.loc[rows_ok, :]
    elif choice == "c":
        # only cols filtered
        return df_clean.loc[:, cols_ok]
    else:  # "b"
        # both filtered, using original percentages
        return df_clean.loc[rows_ok, cols_ok]

def strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    # print('Stripping whitespace from column names and cell values...')
   
    # Work on a copy for safety
    df_clean = df.copy()

    # 1) Strip whitespace from column names
    df_clean.columns = df_clean.columns.str.strip()

    # 2) Strip whitespace inside cells (only object/string columns)
    for col in df_clean.columns:
        if df_clean[col].dtype == "object":
            df_clean[col] = df_clean[col].astype(str).str.strip()

    return df_clean

def normalize_missing_values(df):

    df_clean = df.copy()

# Add more patterns as needed   
    missing_patterns = [
        r"^\s*$",     # empty / whitespace
        r"(?i)^na$",  
        r"(?i)^n/a$",
        r"(?i)^nan$",
        r"(?i)^null$",
        r"(?i)^none$",
        r"^\?$",
        r"^-$",
        r"^\.$",
    ]

    for pattern in missing_patterns:
        df_clean = df_clean.replace(pattern, pd.NA, regex=True)

    return df_clean

def fix_decimal_commas(df: pd.DataFrame) -> pd.DataFrame:

    df_clean = df.copy()

    for col in df_clean.columns:
        if df_clean[col].dtype == "object":  
            # Replace comma-decimal only if the value looks like a number
            df_clean[col] = (
                df_clean[col]
                .str.replace(r"(?<=\d),(?=\d)", ".", regex=True)  # 1,25 -> 1.25
            )

            # Convert to numeric where possible
            try:
                df_clean[col] = pd.to_numeric(df_clean[col])
            except Exception:
                #Leave column unchanged if conversion fails
                df_clean[col] = df_clean[col]


    return df_clean

def extract_numeric_and_unit(df: pd.DataFrame) -> pd.DataFrame:
    import re

    df_clean = df.copy()

    # 1) value + unit in the SAME CELL, e.g. "10 mA", "5,5 V"
    value_pattern = re.compile(
        r"^\s*([+-]?(?:\d+(?:[.,]\d*)?|\d*[.,]\d+))\s*([A-Za-zµ°%]+)\s*$"
    )

    # 2) unit in the HEADER:
    #    - "Current, A"
    #    - "Voltage (V)"
    #    - "Force [N]"
    #    - "Voltage_V"
    #    - "Current_A"
    header_pattern = re.compile(
        r"""
        ^\s*
        (.+?)                               # group 1: base name (lazy)
        (?:                                 # unit part:
            [,\(\[]\s*([A-Za-zµ°%]+)\s*[\)\]]?   # case 1: "Name, A" / "Name (A)" / "Name [A]"
            |
            _([A-Za-zµ°%]+)                 # case 2: "Name_A"
        )
        \s*$
        """,
        re.VERBOSE
    )

    cols = list(df_clean.columns)
    new_columns_order = []

    for col in cols:
        series = df_clean[col]
        did_split = False

        # ---------- CASE 1: value + unit in the cell ----------
        if series.dtype == "object":
            s = series.astype(str)
            extracted = s.str.extract(value_pattern)

            if not extracted.isna().all().all():
                base_name = str(col).strip() or "col"

                num_col = f"{base_name}_value"
                unit_col = f"{base_name}_unit"
                suffix = 2
                while num_col in df_clean.columns or unit_col in df_clean.columns:
                    num_col = f"{base_name}_{suffix}_value"
                    unit_col = f"{base_name}_{suffix}_unit"
                    suffix += 1

                nums = extracted[0].str.replace(",", ".", regex=False)
                df_clean[num_col] = pd.to_numeric(nums, errors="coerce")
                df_clean[unit_col] = extracted[1]

                new_columns_order.extend([num_col, unit_col])
                did_split = True

        if did_split:
            continue

        # ---------- CASE 2: unit in the header ----------
        m = header_pattern.match(str(col))
        if m:
            base_name = m.group(1).strip() or "col"
            header_unit = (m.group(2) or m.group(3)).strip()  # <--- IMPORTANT

            num_col = f"{base_name}_value"
            unit_col = f"{base_name}_unit"
            suffix = 2
            while num_col in df_clean.columns or unit_col in df_clean.columns:
                num_col = f"{base_name}_{suffix}_value"
                unit_col = f"{base_name}_{suffix}_unit"
                suffix += 1

            data = df_clean[col]
            if data.dtype == "object":
                data = data.astype(str).str.replace(",", ".", regex=False)
            df_clean[num_col] = pd.to_numeric(data, errors="coerce")
            df_clean[unit_col] = header_unit

            new_columns_order.extend([num_col, unit_col])
        else:
            new_columns_order.append(col)

    df_clean = df_clean[new_columns_order]
    return df_clean

def convert_units_to_SI(df: pd.DataFrame) -> pd.DataFrame:

    import math

    df_clean = df.copy()

    def _convert_one(value, unit):
        if pd.isna(value) or pd.isna(unit):
            return value, unit

        try:
            v = float(value)
        except (TypeError, ValueError):
            return value, unit

        u = str(unit).strip()
        u = u.replace("°", "deg")  # normalize degrees
        u = u.replace("µ", "u")    # normalize micro
        u = u.lower()

        # ---- temperature -> K ----
        if u in ("degc", "c", "celsius",):
            return v + 273.15, "K"
        if u in ("degf", "fahrenheit",):
            return (v - 32.0) * 5.0 / 9.0 + 273.15, "K"
        if u in ("degk", "k", "kelvin",):
            return v, "K"

        # ---- length -> m ----
        length_units = {
            "mm": 1e-3,
            "cm": 1e-2,
            "m": 1.0,
            "km": 1e3,
        }
        if u in length_units:
            return v * length_units[u], "m"

        # ---- mass -> kg ----
        mass_units = {
            "mg": 1e-6,
            "g": 1e-3,
            "kg": 1.0,
            "t": 1e3,
        }
        if u in mass_units:
            return v * mass_units[u], "kg"

        # ---- time -> s ----
        time_units = {
            "ms": 1e-3,
            "s": 1.0,
            "min": 60.0,
            "h": 3600.0,
        }
        if u in time_units:
            return v * time_units[u], "s"

        # ---- pressure -> Pa ----
        pressure_units = {
            "pa": 1.0,
            "kpa": 1e3,
            "mpa": 1e6,
            "bar": 1e5,
            "mbar": 1e2,
            "atm": 101325.0,
            "psi": 6894.757,
        }
        if u in pressure_units:
            return v * pressure_units[u], "Pa"

        # ---- force -> N ----
        force_units = {
            "n": 1.0,
            "kn": 1e3,
        }
        if u in force_units:
            return v * force_units[u], "N"

        # ---- energy -> J ----
        energy_units = {
            "j": 1.0,
            "kj": 1e3,
        }
        if u in energy_units:
            return v * energy_units[u], "J"

        # ---- percentage -> fraction (0–1) ----
        if u in ("%", "pct"):
            return v / 100.0, "1"   # dimensionless
        
        # ---- voltage -> V ----
        voltage_units = {
            "v": 1.0,
            "mv": 1e-3,
            "kv": 1e3,
        }
        if u in voltage_units:
            return v * voltage_units[u], "V"

        # ---- frequency -> Hz ----
        freq_units = {
            "hz": 1.0,
            "khz": 1e3,
            "mhz": 1e6,
            "ghz": 1e9,
        }
        if u in freq_units:
            return v * freq_units[u], "Hz"

        # ---- electric current -> A ----
        current_units = {
            "a": 1.0,
            "ma": 1e-3,
            "ka": 1e3,
        }
        if u in current_units:
            return v * current_units[u], "A"

        # ---- resistance -> ohm ----
        resistance_units = {
            "ohm": 1.0,
            "kohm": 1e3,
            "mohm": 1e6,
            "ω": 1.0,      # lowercase omega
            "kω": 1e3,
            "mω": 1e6,
        }
        if u in resistance_units:
            return v * resistance_units[u], "ohm"

        # ---- capacitance -> F ----
        capacitance_units = {
            "f": 1.0,
            "mf": 1e-3,
            "uf": 1e-6,
            "nf": 1e-9,
            "pf": 1e-12,
        }
        if u in capacitance_units:
            return v * capacitance_units[u], "F"

        # ---- wavelength -> meters ----
        wavelength_units = {
            "m": 1.0,
            "mm": 1e-3,
            "um": 1e-6,
            "µm": 1e-6,
            "nm": 1e-9,
        }
        if u in wavelength_units:
            return v * wavelength_units[u], "m"

        # unknown unit -> leave as is
        return value, unit

    # Look for <base>_value + <base>_unit pairs
    cols = list(df_clean.columns)
    for col in cols:
        if col.endswith("_value"):
            base = col[:-6]  # remove "_value"
            unit_col = base + "_unit"
            if unit_col in df_clean.columns:
                # make sure numeric column is float BEFORE assigning converted values
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").astype("float64")

                for idx, (val, unit) in df_clean[[col, unit_col]].iterrows():
                    new_val, new_unit = _convert_one(val, unit)
                    df_clean.at[idx, col] = new_val
                    df_clean.at[idx, unit_col] = new_unit

                # (optional) one more coerce if you really want to be safe:
                # df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    return df_clean

def remove_duplicate_rows(df):
    df_clean = df.copy()

    # Detect duplicates anywhere in the file (not only next to each other)
    dup_mask = df_clean.duplicated(keep="first")

    # Remove ALL duplicate rows, keep only the first appearance
    df_clean = df_clean[~dup_mask]

    return df_clean

def _ask_yes_no(prompt: str) -> bool:
    """
    Ask until user types Y/Yes or N/No.
    Returns True for yes, False for no.
    """
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("Please type y or n.")

def move_rows_or_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    1) Ask ONCE: move rows or columns
    2) Show layout
    3) Ask: which one to move and to where (two numbers)
    4) Do the move, show new layout
    5) Ask: move another? yes/no (forced Y/N)
    6) Repeat 3–5 until user says no, then return df
    """
    df_clean = df.copy()

    # ---- 1) choose rows or columns (once) ----
    while True:
        kind = input("What do you want to move? (r)ows or (c)olumns: ").strip().lower()
        if kind in ("r", "c"):
            break
        print("Please type 'r' for rows or 'c' for columns.")

    # ---- 2) MOVING ROWS ----
    if kind == "r":
        while True:
            n_rows = len(df_clean)
            if n_rows <= 1:
                print("Not enough rows to move.")
                break

            print("\nCurrent rows (index shown on the left):")
            _print_rows_preview(df_clean)

            try:
                pair = input(
                    f"\nWhich row do you want to move and to where? "
                    f"(enter two numbers 1–{n_rows}, e.g. '2 5'): "
                )
                src_str, dest_str = pair.split()
                src = int(src_str)
                dest = int(dest_str)
            except ValueError:
                print("Please enter TWO integers separated by space, like: 2 5")
                continue

            if not (1 <= src <= n_rows and 1 <= dest <= n_rows):
                print("Row numbers out of range.")
                continue

            indices = list(range(n_rows))
            row_idx = indices.pop(src - 1)
            indices.insert(dest - 1, row_idx)
            df_clean = df_clean.iloc[indices].reset_index(drop=True)

            print("\nNew row layout:")
            _print_rows_preview(df_clean)

            if not _ask_yes_no("\nDo you want to move another row? (y/n): "):
                break

    # ---- 3) MOVING COLUMNS ----
    else:  # kind == "c"
        while True:
            cols = list(df_clean.columns)
            n_cols = len(cols)
            if n_cols <= 1:
                print("Not enough columns to move.")
                break

            print("\nCurrent columns order:")
            for i, c in enumerate(cols, 1):
                print(f"  {i}) {c}")

            print("\nCurrent table:")
            _print_rows_preview(df_clean)

            try:
                pair = input(
                    f"\nWhich column do you want to move and to where? "
                    f"(enter two numbers 1–{n_cols}, e.g. '1 3'): "
                )
                src_str, dest_str = pair.split()
                src = int(src_str)
                dest = int(dest_str)
            except ValueError:
                print("Please enter TWO integers separated by space, like: 1 3")
                continue

            if not (1 <= src <= n_cols and 1 <= dest <= n_cols):
                print("Column numbers out of range.")
                continue

            col_name = cols.pop(src - 1)
            cols.insert(dest - 1, col_name)
            df_clean = df_clean[cols]

            print("\nNew column layout:")
            _print_rows_preview(df_clean)

            if not _ask_yes_no("\nDo you want to move another column? (y/n): "):
                break

    return df_clean

def _print_rows_preview(df: pd.DataFrame, max_rows: int = 20) -> None:
    """
    Print a preview of the dataframe.
    - If small: print everything
    - If large: print head and tail
    - Index is shown starting from 1 (not 0)
    """
    if df is None or df.empty:
        print("<empty table>")
        return

    df_show = df.reset_index(drop=True).copy()
    df_show.index = df_show.index + 1  # 1-based index

    n = len(df_show)
    if n <= max_rows:
        print(df_show)
    else:
        half = max_rows // 2
        print(df_show.head(half))
        print("...")
        print(df_show.tail(max_rows - half))

def _choose_column(columns, prompt):
    while True:
        print(prompt)
        for i, col in enumerate(columns, start=1):
            print(f"[{i}] {col}")

        choice = input("Enter column number (or 'q' to cancel): ").strip().lower()

        if choice == "q":
            return None

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(columns):
                return columns[idx - 1]

        print("Invalid choice. Please enter a valid number or 'q'.\n")

def _choose_multiple_columns(columns, prompt):
    while True:
        print(prompt)
        for i, col in enumerate(columns, start=1):
            print(f"[{i}] {col}")

        choice = input(
            "Enter column number(s) separated by commas/spaces (or 'q' to cancel): "
        ).strip().lower()

        if choice == "q":
            return None

        tokens = re.split(r"[,\s]+", choice)
        tokens = [t for t in tokens if t]

        selected = []

        valid = True
        for t in tokens:
            if t.isdigit():
                idx = int(t)
                if 1 <= idx <= len(columns):
                    selected.append(columns[idx - 1])
                else:
                    print(f"Invalid index: {t}")
                    valid = False
            else:
                print(f"Ignoring invalid token: {t!r}")
                valid = False

        if selected and valid:
            return selected
        else:
            print("\nPlease enter only valid column numbers.\n")

def _style_axes(ax, x_label, y_label, title):
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    for spine in ax.spines.values():
        spine.set_visible(True)

    ax.tick_params(direction="in", top=True, right=True)
    # Grid is now controlled by user choice

def plot_data(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """
    Plot action:
      - choose X
      - choose one or more Y
      - choose plot type
      - choose axis scales, grid, labels, title
      - save PNG to Plots/  (CSV not touched)
    """
    if df.empty:
        print("DataFrame is empty, nothing to plot.")
        return df

    all_cols = list(df.columns)

    # X
    x_col = _choose_column(all_cols, "\nChoose X-axis column:")
    if x_col is None:
        return df

    # Y (multi)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        numeric_cols = all_cols

    y_cols = _choose_multiple_columns(numeric_cols, "\nChoose Y-axis column(s):")
    if not y_cols:
        return df

    # ----- plot type (forced 1/2/3) -----
    while True:
        print("\nChoose plot type:")
        print("[1] Line (y vs x)")
        print("[2] Scatter (y vs x)")
        print("[3] Bar (y vs x)")
        plot_choice = input("Enter number (1/2/3): ").strip()
        if plot_choice in ("1", "2", "3"):
            break
        print("Please enter 1, 2 or 3.")

    x_raw = df[x_col]
    x_num = pd.to_numeric(x_raw, errors="coerce")
    x_is_mostly_numeric = x_num.notna().mean() > 0.8

    fig, ax = plt.subplots()

    # line / scatter (multi-Y)
    if plot_choice in ("1", "2"):
        if not x_is_mostly_numeric:
            print("X column is not numeric enough for line/scatter. Try bar plot instead.")
            plt.close(fig)
            return df

        any_plotted = False
        for y_col in y_cols:
            y_raw = df[y_col]
            y_num = pd.to_numeric(y_raw, errors="coerce")
            mask = x_num.notna() & y_num.notna()
            x = x_num[mask]
            y = y_num[mask]

            if y.empty:
                print(f"No valid numeric data for {y_col}, skipping.")
                continue

            if plot_choice == "1":
                ax.plot(x, y, label=y_col)
            else:
                ax.scatter(x, y, label=y_col)

            any_plotted = True

        if not any_plotted:
            print("Nothing to plot after cleaning data.")
            plt.close(fig)
            return df

        title = f"{', '.join(y_cols)} vs {x_col} ({'line' if plot_choice == '1' else 'scatter'})"
        _style_axes(ax, x_col, ", ".join(y_cols), title)
        if len(y_cols) > 1:
            ax.legend()

    # bar (use first Y)
    elif plot_choice == "3":
        if len(y_cols) > 1:
            print("Bar plot: using only the first selected Y column.")
        y_col = y_cols[0]

        y_raw = df[y_col]
        y_num = pd.to_numeric(y_raw, errors="coerce")

        if x_is_mostly_numeric:
            mask = x_num.notna() & y_num.notna()
            x = x_num[mask]
            y = y_num[mask]
        else:
            mask = y_num.notna()
            x = x_raw[mask].astype(str)
            y = y_num[mask]

        if y.empty:
            print("No valid data to plot.")
            plt.close(fig)
            return df

        ax.bar(x, y)
        title = f"{y_col} vs {x_col} (bar)"
        _style_axes(ax, x_col, y_col, title)
        plt.xticks(rotation=45)

    # ===== axis scales: linear / log =====
    print("\nAxis scale options:")

    # X scale (force 1/2, default 1 on empty)
    while True:
        print("X-axis: [1] linear  [2] log")
        x_choice = input("Choose X-axis scale [1]: ").strip()
        if x_choice in ("", "1", "2"):
            break
        print("Please type 1 for linear or 2 for log.")

    if x_choice == "2":
        ax.set_xscale("log")
    else:
        ax.set_xscale("linear")

    # Y scale (force 1/2, default 1 on empty)
    while True:
        print("Y-axis: [1] linear  [2] log")
        y_choice = input("Choose Y-axis scale [1]: ").strip()
        if y_choice in ("", "1", "2"):
            break
        print("Please type 1 for linear or 2 for log.")

    if y_choice == "2":
        ax.set_yscale("log")
    else:
        ax.set_yscale("linear")

    # ----- grid toggle (force 1/2, default 1) -----
    while True:
        print("\nGrid options:")
        print("[1] Grid ON")
        print("[2] Grid OFF")
        grid_choice = input("Enable grid? [1]: ").strip()
        if grid_choice in ("", "1", "2"):
            break
        print("Please type 1 for ON or 2 for OFF.")

    ax.grid(grid_choice != "2")

    plt.tight_layout()

    print("\n----- Plot customization -----")

    # X label
    default_x_label = x_col
    x_label = input(f"X-axis label [{default_x_label}]: ").strip()
    if not x_label:
        x_label = default_x_label
    ax.set_xlabel(x_label)

    # Y label (if multi-Y, default = comma-separated)
    default_y_label = ", ".join(y_cols)
    y_label = input(f"Y-axis label [{default_y_label}]: ").strip()
    if not y_label:
        y_label = default_y_label
    ax.set_ylabel(y_label)

    # Legend toggle (force y/n with defaults)
    if len(y_cols) > 1:
        # default: yes
        while True:
            add_legend = input("Add legend? (y/n) [y]: ").strip().lower()
            if add_legend in ("", "y", "yes", "n", "no"):
                break
            print("Please type y or n.")
        if add_legend in ("", "y", "yes"):
            ax.legend()
    else:
        # default: no
        while True:
            add_legend = input("Add legend? (y/n) [n]: ").strip().lower()
            if add_legend in ("", "y", "yes", "n", "no"):
                break
            print("Please type y or n.")
        if add_legend in ("y", "yes"):
            ax.legend()

    # Title toggle + custom title (force y/n with default yes)
    while True:
        enable_title = input("Add title? (y/n) [y]: ").strip().lower()
        if enable_title in ("", "y", "yes", "n", "no"):
            break
        print("Please type y or n.")

    if enable_title in ("", "y", "yes"):
        default_title = ax.get_title() or ""
        custom_title = input(f"Title [{default_title}]: ").strip()
        if not custom_title:
            custom_title = default_title
        ax.set_title(custom_title)
    else:
        ax.set_title("")  # clear title

    # ===== ASK USER WHERE TO SAVE PNG (relative to project folder) =====
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    base = os.path.splitext(os.path.basename(file_path))[0]
    y_part = "_".join(y_cols).replace(" ", "_").replace("/", "_")
    default_name = f"{base}_{x_col}_vs_{y_part}.png"

    print("\n==============================")
    print("Saving plot PNG")
    print("==============================")
    print("Working directory:", project_root)
    print("\nEnter output PNG path relative to the Working folder.")
    print("Examples:")
    print(f"   {default_name}")
    print(f"   Plots/{default_name}")
    print("   figures/run1/iv_curve.png\n")

    while True:
        out = input(f"Output PNG path [{default_name}]: ").strip()

        if not out:
            out = default_name

        if not out.lower().endswith(".png"):
            print("Output must end with .png")
            continue

        png_path = os.path.join(project_root, out)
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        break

    plt.savefig(png_path, dpi=300)
    print("\nPlot saved as:\n  ", png_path)

    plt.close(fig)
    return df

def _latex_escape(value) -> str:
    if pd.isna(value):
        return ""
    s = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s

def generate_latex_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Let the user pick columns + (optionally) row range and save a standalone
    LaTeX file (.tex) containing a full document with a single table.
    Does NOT modify df.
    """
    import os

    if df.empty:
        print("DataFrame is empty, nothing to export.")
        return df

    all_cols = list(df.columns)

    # choose columns
    from_cols = _choose_multiple_columns(all_cols, "\nChoose column(s) for LaTeX table:")
    if not from_cols:
        return df

    n_rows = len(df)
    print(f"\nData has {n_rows} rows.")
    use_all = input("Use ALL rows? (y/n) [y]: ").strip().lower()

    if use_all in ("", "y", "yes"):
        df_sub = df[from_cols]
    else:
        try:
            start = int(input("Start row (1-based): ").strip())
            end = int(input("End row (1-based, inclusive): ").strip())
        except ValueError:
            print("Invalid row numbers. Using all rows instead.")
            df_sub = df[from_cols]
        else:
            start = max(1, start)
            end = min(n_rows, end)
            if start > end:
                print("Start > end, using all rows instead.")
                df_sub = df[from_cols]
            else:
                df_sub = df.iloc[start - 1:end][from_cols]

    # caption / label / alignment
    print("\n----- LaTeX table settings -----")
    caption = input("Caption (optional): ").strip()
    label = input("Label (without \\label{}), e.g. table:results (optional): ").strip()

    align_choice = input("Column alignment (l/c/r) for ALL columns [c]: ").strip().lower()
    if align_choice not in ("l", "r", "c"):
        align_choice = "c"
    col_spec = "|" + "|".join(align_choice for _ in from_cols) + "|"

    # ---------- build LaTeX as a FULL document ----------
    lines = []
    lines.append(r"\documentclass{article}")
    lines.append(r"\usepackage[utf8]{inputenc}")
    lines.append(r"\usepackage{siunitx}")  # handy for physics, ok if unused
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append("")

    lines.append(r"\begin{table}[htbp]")
    lines.append(r"  \centering")
    if caption:
        lines.append(f"  \\caption{{{_latex_escape(caption)}}}")
    if label:
        lines.append(f"  \\label{{{label}}}")
    lines.append(f"  \\begin{{tabular}}{{{col_spec}}}")
    lines.append(r"    \hline")

    # Header row
    header = " & ".join(_latex_escape(c) for c in from_cols) + r" \\"
    lines.append("    " + header)
    lines.append(r"    \hline")

    # Data rows
    for _, row in df_sub.iterrows():
        row_str = " & ".join(_latex_escape(v) for v in row[from_cols]) + r" \\"
        lines.append("    " + row_str)
        lines.append(r"    \hline")
    lines.append(r"  \end{tabular}")
    lines.append(r"\end{table}")
    lines.append("")
    lines.append(r"\end{document}")

    latex_str = "\n".join(lines)

    # ask where to save, relative to project root (one level above Scripts)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print("\n==============================")
    print("Saving LaTeX table (standalone document)")
    print("==============================")
    print("Project directory:", project_root)
    print("\nEnter output .tex path relative to the Project folder.")
    print("Examples:")
    print("   table.tex")
    print("   Latex/tested_10.tex\n")

    while True:
        out = input("Output .tex path: ").strip()
        if not out.lower().endswith(".tex"):
            print("Output must end with .tex")
            continue

        tex_path = os.path.join(project_root, out)
        os.makedirs(os.path.dirname(tex_path), exist_ok=True)
        break

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_str)

    print("\nLaTeX table saved as:\n  ", tex_path)
    print("You can compile this file directly (pdflatex / LaTeX Workshop).")
    return df
