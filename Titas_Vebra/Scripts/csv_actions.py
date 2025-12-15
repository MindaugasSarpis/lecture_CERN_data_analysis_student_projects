import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from pathlib import Path

def remove_rows_and_columns(df: pd.DataFrame) -> pd.DataFrame:

    # Works on a copy so you don't mutate original by accident
    df_clean = df.copy()
    df_clean = df_clean.replace(r'^\s*$', np.nan, regex=True)

    # What to remove
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

    # compute on original df_clean (before any dropping)
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
    df_clean = df.copy()

    # Strip whitespace from column names
    df_clean.columns = df_clean.columns.map(lambda c: c.strip() if isinstance(c, str) else c)

    # Strip whitespace inside cells ONLY for real strings (do not stringify NA/None)
    obj_cols = df_clean.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        df_clean[col] = df_clean[col].apply(
            lambda v: v.strip() if isinstance(v, str) else v
        )

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

    def _maybe_convert(v):
        # Keep missing as-is
        if pd.isna(v):
            return v

        # Only touch real strings
        if not isinstance(v, str):
            return v

        s = v.strip()
        if s == "":
            return v  # keep empty string as empty string

        # US mixed: 1,234.56 -> 1234.56
        if re.fullmatch(r"[+-]?\d{1,3}(?:,\d{3})+\.\d+", s):
            s2 = s.replace(",", "")
            return float(s2)

        # EU mixed: 1.234,56 -> 1234.56
        if re.fullmatch(r"[+-]?\d{1,3}(?:\.\d{3})+,\d+", s):
            s2 = s.replace(".", "").replace(",", ".")
            return float(s2)

        # US thousands: 10,000 -> 10000
        if re.fullmatch(r"[+-]?\d{1,3}(?:,\d{3})+", s):
            s2 = s.replace(",", "")
            return float(s2)

        # EU decimal: 12,5 -> 12.5
        if re.fullmatch(r"[+-]?\d+,\d+", s):
            s2 = s.replace(",", ".")
            return float(s2)

        # Plain numeric: 1234.56 or 1234
        if re.fullmatch(r"[+-]?\d+(?:\.\d+)?", s):
            return float(s)

        # Not numeric-looking -> leave untouched
        return v

    obj_cols = df_clean.select_dtypes(include=["object"]).columns
    for col in obj_cols:
        df_clean[col] = df_clean[col].apply(_maybe_convert)

    return df_clean

def extract_numeric_and_unit(df: pd.DataFrame) -> pd.DataFrame:

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
    df_clean = df.copy()

    def _norm_unit(u: pd.Series) -> pd.Series:
        u = u.astype("string").str.strip()
        u = u.str.replace("°", "deg", regex=False)
        u = u.str.replace("µ", "u", regex=False)
        return u.str.lower()

    FACTOR_MAPS = {
        "m": {"mm": 1e-3, "cm": 1e-2, "m": 1.0, "km": 1e3},
        "kg": {"mg": 1e-6, "g": 1e-3, "kg": 1.0, "t": 1e3},
        "s": {"ms": 1e-3, "s": 1.0, "min": 60.0, "h": 3600.0},
        "pa": {"pa": 1.0, "kpa": 1e3, "mpa": 1e6, "bar": 1e5, "mbar": 1e2, "atm": 101325.0, "psi": 6894.757},
        "n": {"n": 1.0, "kn": 1e3},
        "j": {"j": 1.0, "kj": 1e3},
        "v": {"v": 1.0, "mv": 1e-3, "kv": 1e3},
        "hz": {"hz": 1.0, "khz": 1e3, "mhz": 1e6, "ghz": 1e9},
        "a": {"a": 1.0, "ma": 1e-3, "ka": 1e3},
        "ohm": {"ohm": 1.0, "kohm": 1e3, "mohm": 1e6, "ω": 1.0, "kω": 1e3, "mω": 1e6, "Ω": 1.0, "kΩ": 1e3, "mΩ": 1e6},
        "f": {"f": 1.0, "mf": 1e-3, "uf": 1e-6, "nf": 1e-9, "pf": 1e-12},
        # if you really need wavelength, keep it, but it MUST NOT double-apply
        "m_wl": {"m": 1.0, "mm": 1e-3, "um": 1e-6, "nm": 1e-9},
    }

    for col in list(df_clean.columns):
        if not str(col).endswith("_value"):
            continue

        base = str(col)[:-6]
        unit_col = base + "_unit"
        if unit_col not in df_clean.columns:
            continue

        v = pd.to_numeric(df_clean[col], errors="coerce").astype("float64")
        u_raw = df_clean[unit_col].astype("string").copy()
        u = _norm_unit(u_raw)

        # temperature -> K
        mask_c = u.isin(["degc", "c", "celsius"])
        if mask_c.any():
            v.loc[mask_c] = v.loc[mask_c] + 273.15
            u_raw.loc[mask_c] = "K"
            u.loc[mask_c] = "k"

        mask_f = u.isin(["degf", "fahrenheit"])
        if mask_f.any():
            v.loc[mask_f] = (v.loc[mask_f] - 32.0) * 5.0 / 9.0 + 273.15
            u_raw.loc[mask_f] = "K"
            u.loc[mask_f] = "k"

        mask_k = u.isin(["degk", "k", "kelvin"])
        if mask_k.any():
            u_raw.loc[mask_k] = "K"
            u.loc[mask_k] = "k"

        # percent -> fraction
        mask_pct = u.isin(["%", "pct"])
        if mask_pct.any():
            v.loc[mask_pct] = v.loc[mask_pct] / 100.0
            u_raw.loc[mask_pct] = "1"
            u.loc[mask_pct] = "1"

        def _apply_factor_map(mapping: dict, out_unit_label: str):
            nonlocal u, u_raw, v
            factors = u.map(mapping)
            mask = factors.notna()
            if mask.any():
                v.loc[mask] = v.loc[mask] * factors.loc[mask].astype("float64")
                u_raw.loc[mask] = out_unit_label
                # CRITICAL: update normalized units so later maps don't re-apply
                u.loc[mask] = str(out_unit_label).lower()

        _apply_factor_map(FACTOR_MAPS["m"], "m")
        _apply_factor_map(FACTOR_MAPS["kg"], "kg")
        _apply_factor_map(FACTOR_MAPS["s"], "s")
        _apply_factor_map(FACTOR_MAPS["pa"], "Pa")
        _apply_factor_map(FACTOR_MAPS["n"], "N")
        _apply_factor_map(FACTOR_MAPS["j"], "J")
        _apply_factor_map(FACTOR_MAPS["v"], "V")
        _apply_factor_map(FACTOR_MAPS["hz"], "Hz")
        _apply_factor_map(FACTOR_MAPS["a"], "A")
        _apply_factor_map(FACTOR_MAPS["ohm"], "ohm")
        _apply_factor_map(FACTOR_MAPS["f"], "F")
        _apply_factor_map(FACTOR_MAPS["m_wl"], "m")

        df_clean[col] = v
        df_clean[unit_col] = u_raw

    return df_clean

def remove_duplicate_rows(df):
    df_clean = df.copy()

    # Detect duplicates anywhere in the file
    dup_mask = df_clean.duplicated(keep="first")

    # Remove ALL duplicate rows, keep only the first appearance
    df_clean = df_clean[~dup_mask]

    return df_clean

# Helper if user inputs something other than y/n
def _ask_yes_no(prompt: str) -> bool:
    """
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
  
    df_clean = df.copy()

    # ---- 1) choose rows or columns (once) ----
    while True:
        kind = input("What do you want to move? (r)ows or (c)olumns: ").strip().lower()
        if kind in ("r", "c"):
            break
        print("Please type 'r' for rows or 'c' for columns.")

    # ---- 2) moving rows ----
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

    # ---- 3) moving columns ----
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

# Helper to print dataframe preview
def _print_rows_preview(df: pd.DataFrame, max_rows: int = 20) -> None:
    """
    Print a preview of the dataframe.
    - If small: print everything
    - If large: print head and tail
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

def plot_data(df: pd.DataFrame, file_path: str, config: dict | None = None) -> pd.DataFrame:
    
    if df.empty:
        print("DataFrame is empty, nothing to plot.")
        return df

    all_cols = list(df.columns)

    # Optional config (non-interactive)
    cfg = config or {}
    config_mode = bool(cfg)
    
    # X
    x_col = cfg.get("x_col") or _choose_column(all_cols, "\nChoose X-axis column:")
    if x_col is None:
        return df

    # Y (multi)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        numeric_cols = all_cols

    y_cols = cfg.get("y_cols") or _choose_multiple_columns(numeric_cols, "\nChoose Y-axis column(s):")
    if not y_cols:
        return df

    # ----- plot type -----
    if config_mode:
        plot_type = (cfg.get("plot_type") or "line").strip().lower()
        plot_choice = {"line": "1", "scatter": "2", "bar": "3"}.get(plot_type, "1")
    else:
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
    if config_mode:
        ax.set_xscale((cfg.get("x_scale") or "linear").strip().lower())
        ax.set_yscale((cfg.get("y_scale") or "linear").strip().lower())
    else:
        print("\nAxis scale options:")

        while True:
            print("X-axis: [1] linear  [2] log")
            x_choice = input("Choose X-axis scale [1]: ").strip()
            if x_choice in ("", "1", "2"):
                break
            print("Please type 1 for linear or 2 for log.")
        ax.set_xscale("log" if x_choice == "2" else "linear")

        while True:
            print("Y-axis: [1] linear  [2] log")
            y_choice = input("Choose Y-axis scale [1]: ").strip()
            if y_choice in ("", "1", "2"):
                break
            print("Please type 1 for linear or 2 for log.")
        ax.set_yscale("log" if y_choice == "2" else "linear")

    # ----- grid toggle (default 1 on empty) -----
    if config_mode:
        ax.grid(bool(cfg.get("grid", True)))
    else:
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

    # ----- Plot customization -----
    if config_mode:
        ax.set_xlabel(cfg.get("x_label") or x_col)
        ax.set_ylabel(cfg.get("y_label") or ", ".join(y_cols))

        show_legend = bool(cfg.get("legend", True))
        if show_legend and (len(y_cols) > 1 or cfg.get("legend_force", False)):
            ax.legend()

        if cfg.get("title") is not None:
            ax.set_title(cfg.get("title") or "")
    else:
        print("\n----- Plot customization -----")

        default_x_label = x_col
        x_label = input(f"X-axis label [{default_x_label}]: ").strip()
        if not x_label:
            x_label = default_x_label
        ax.set_xlabel(x_label)

        default_y_label = ", ".join(y_cols)
        y_label = input(f"Y-axis label [{default_y_label}]: ").strip()
        if not y_label:
            y_label = default_y_label
        ax.set_ylabel(y_label)

        # Legend toggle
        if len(y_cols) > 1:
            while True:
                add_legend = input("Add legend? (y/n) [y]: ").strip().lower()
                if add_legend in ("", "y", "yes", "n", "no"):
                    break
            if add_legend in ("", "y", "yes"):
                ax.legend()
        else:
            while True:
                add_legend = input("Add legend? (y/n) [n]: ").strip().lower()
                if add_legend in ("", "y", "yes", "n", "no"):
                    break
            if add_legend in ("y", "yes"):
                ax.legend()

        while True:
            enable_title = input("Add title? (y/n) [y]: ").strip().lower()
            if enable_title in ("", "y", "yes", "n", "no"):
                break
        if enable_title in ("", "y", "yes"):
            default_title = ax.get_title() or ""
            custom_title = input(f"Title [{default_title}]: ").strip()
            ax.set_title(custom_title or default_title)
        else:
            ax.set_title("")

    # ===== asks user where to save png (relative to working folder) =====
    project_root = Path(__file__).resolve().parent.parent

    # ===== save png =====
    base = os.path.splitext(os.path.basename(file_path))[0]
    y_part = "_".join(y_cols).replace(" ", "_").replace("/", "_")
    default_name = f"{base}_{x_col}_vs_{y_part}.png"

    if config_mode:
        out = cfg.get("output_png") or default_name
    else:
        print("\n==============================")
        print("Saving plot PNG")
        print("==============================")
        print("Project directory:", project_root)
        print("\nEnter output PNG path relative to the Project folder.")
        print("Examples:")
        print(f"   {default_name}")
        print(f"   Plots/{default_name}")
        print("   figures/run1/iv_curve.png\n")
        out = input(f"Output PNG path [{default_name}]: ").strip() or default_name

    if not out.lower().endswith(".png"):
        out += ".png"

    png_path = project_root / out
    os.makedirs(os.path.dirname(png_path), exist_ok=True)

    plt.savefig(png_path, dpi=300)
    print("\nPlot saved as:\n  ", png_path)

    plt.close(fig)
    return df

# Helper to escape LaTeX special characters
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

def generate_latex_table(df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:

    if df.empty:
        print("DataFrame is empty, nothing to export.")
        return df

    all_cols = list(df.columns)

    # Optional config (non-interactive)
    # config example:
    # {"columns": ["A","B"], "use_all_rows": true, "row_start": 1, "row_end": 20, "caption": "...", "label": "table:...", "align": "c", "output_tex": "Latex/table.tex"}
    cfg = config or {}

    # choose columns
    from_cols = cfg.get("columns") or _choose_multiple_columns(all_cols, "\nChoose column(s) for LaTeX table:")
    if not from_cols:
        return df

    n_rows = len(df)
    print(f"\nData has {n_rows} rows.")
    use_all = ("y" if cfg.get("use_all_rows") is True else "n" if cfg.get("use_all_rows") is False else input("Use ALL rows? (y/n) [y]: ").strip().lower())

    if use_all in ("", "y", "yes"):
        df_sub = df[from_cols]
    else:
        try:
            start = int(cfg.get("row_start") or input("Start row (1-based): ").strip())
            end = int(cfg.get("row_end") or input("End row (1-based, inclusive): ").strip())
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
    caption = cfg.get("caption") if cfg.get("caption") is not None else input("Caption (optional): ").strip()
    label = cfg.get("label") if cfg.get("label") is not None else input("Label (without \\label{}), e.g. table:results (optional): ").strip()

    align_choice = (str(cfg.get("align")).strip().lower() if cfg.get("align") is not None else input("Column alignment (l/c/r) for ALL columns [c]: ").strip().lower())
    if align_choice not in ("l", "r", "c"):
        align_choice = "c"
    col_spec = "|" + "|".join(align_choice for _ in from_cols) + "|"

    # ---------- build LaTeX as a full document ----------
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

    # ask where to save, relative to working root 
    project_root = Path(__file__).resolve().parent.parent

    print("\n==============================")
    print("Saving LaTeX table (standalone document)")
    print("==============================")
    print("Project directory:", project_root)
    print("\nEnter output .tex path relative to the Project folder.")
    print("Examples:")
    print("   table.tex")
    print("   Latex/tested_10.tex\n")

    while True:
        out = (cfg.get("output_tex") if cfg.get("output_tex") is not None else input("Output .tex path: ").strip())
        if not out.lower().endswith(".tex"):
            print("Output must end with .tex")
            continue

        tex_path = project_root / out
        os.makedirs(os.path.dirname(tex_path), exist_ok=True)
        break

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_str)

    print("\nLaTeX table saved as:\n  ", tex_path)
    print("You can compile this file directly (pdflatex / LaTeX Workshop).")
    return df
