import os
import pandas as pd
from pandas.errors import ParserError

Root_dir = os.getcwd()

def _update_cleaning_log(action: str, before_df: pd.DataFrame, after_df: pd.DataFrame, log_entries: list):
    """
    Append human-readable info about what changed during one cleaning action.
    """

    # 1) Remove rows and columns -> list which rows/columns disappeared
    if action == "Remove rows and columns":
        # rows removed: compare index labels before/after,
        # then convert to 1-based positions in the BEFORE table
        keep_mask = before_df.index.isin(after_df.index)
        removed_positions = [i + 1 for i, keep in enumerate(keep_mask) if not keep]

        # columns removed: by name
        removed_cols = [col for col in before_df.columns if col not in after_df.columns]

        log_entries.append(
            f"Remove rows and columns: removed row positions {removed_positions}, "
            f"removed columns {removed_cols}"
        )
        return

    # 2) Strip whitespace -> just note it was done
    if action == "Strip whitespace":
        log_entries.append("Strip whitespace: action performed.")
        return

    # 3) Normalize missing values -> which coordinates became missing
    if action == "Normalize missing values":
        # map index -> 1-based row position for nicer logging
        row_pos = {idx: i + 1 for i, idx in enumerate(before_df.index)}

        changed = []
        for col in before_df.columns:
            if col not in after_df.columns:
                continue

            for idx in before_df.index:
                if idx not in after_df.index:
                    continue

                before_val = before_df.at[idx, col]
                after_val = after_df.at[idx, col]

                # only values that BECAME missing
                if pd.isna(after_val) and not pd.isna(before_val):
                    changed.append((row_pos[idx], col, before_val))

        if changed:
            log_entries.append(
                f"Normalize missing values: normalized {len(changed)} values:"
            )
            for row, col, val in changed:
                log_entries.append(
                    f"  at row {row}, column '{col}': '{val}' -> <missing>"
                )
        else:
            log_entries.append("Normalize missing values: no values changed.")
        return

    # 4) Fix decimal commas -> just note it
    if action == "Fix decimal commas":
        log_entries.append("Fix decimal commas: action performed.")
        return

    # 5) Extract numeric value + units -> just note it
    if action == "Extract numeric value + units":
        log_entries.append("Extract numeric value + units: action performed.")
        return

    # 6) Convert units to SI -> record unit-string changes in *_unit columns
    if action == "Convert units to SI":
        changes = {}
        common_cols = before_df.columns.intersection(after_df.columns)
        common_idx = before_df.index.intersection(after_df.index)

        for col in common_cols:
            if not str(col).endswith("_unit"):
                continue
            for idx in common_idx:
                b_val = before_df.at[idx, col]
                a_val = after_df.at[idx, col]
                if pd.isna(b_val) or pd.isna(a_val):
                    continue
                if b_val != a_val:
                    key = (str(b_val), str(a_val))
                    changes[key] = changes.get(key, 0) + 1

        if changes:
            log_entries.append("Convert units to SI: converted units:")
            for (u_from, u_to), count in changes.items():
                log_entries.append(f"  '{u_from}' -> '{u_to}': {count} values")
        else:
            log_entries.append("Convert units to SI: no unit changes detected.")
        return

    # 7) Clear duplicate rows -> which original row indices were dropped
    if action == "Clear duplicate rows":
        # True where the row is a duplicate of a previous one (this is what pandas drops)
        dup_mask = before_df.duplicated(keep="first")

        removed_positions = [i + 1 for i, is_dup in enumerate(dup_mask) if is_dup]

        if removed_positions:
            log_entries.append(
                f"Clear duplicate rows: dropped duplicate row positions {removed_positions}"
            )
        else:
            log_entries.append("Clear duplicate rows: no duplicates found.")
        return

    # 8) Move rows or columns -> just note it
    if action == "Move rows or columns":
        log_entries.append("Move rows or columns: action performed.")
        return

    # 9) Plot data
    if action == "Plot data":
        log_entries.append("Plot data: plotting was performed.")
        return

    # 10) Generate LaTeX table
    if action == "Generate LaTeX table":
        log_entries.append("Generate LaTeX table: LaTeX table was generated.")
        return

def browse_and_choose_csv():

    start_dir = os.getcwd()
    current_dir = start_dir

    while True:
        print("\n====================================")
        print("Current location:", current_dir)
        print("====================================")

        try:
            entries = os.listdir(current_dir)
        except PermissionError:
            print("No permission for this folder, going back.")
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                print("Already at the top level, cannot go back further.")
            else:
                current_dir = parent
            continue

        dirs = sorted([e for e in entries if os.path.isdir(os.path.join(current_dir, e))])
        csvs = sorted([e for e in entries if e.lower().endswith(".csv")])

        items = [("dir", d) for d in dirs] + [("csv", f) for f in csvs]

        if not items:
            print("(This folder is empty.)")

        # List entries
        for idx, (kind, name) in enumerate(items, 1):
            label = "[DIR]" if kind == "dir" else "[CSV]"
            print(f"{idx}) {label} {name}")

        # Commands info
        print("\nCommands:")
        print("  <number>  -> open folder / select CSV")
        print("  back      -> go back")
        print("  quit      -> exit without selecting a file")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "quit":
            return None

        if choice == "back":
            parent = os.path.dirname(current_dir)
            if parent == current_dir:
                print("Already at the top level.")
            else:
                current_dir = parent
            continue

        if not choice.isdigit():
            print("Please enter a number, 'back', or 'quit'.")
            continue

        n = int(choice)
        if not (1 <= n <= len(items)):
            print("Invalid number.")
            continue

        kind, name = items[n - 1]
        path = os.path.join(current_dir, name)

        if kind == "dir":
            current_dir = path
        else:  # CSV selected
            print(f"\nSelected CSV: {path}")
            return path
    
def choose_csv_actions():

    actions = [
        "Remove rows and columns",
        "Strip whitespace",
        "Normalize missing values",
        "Fix decimal commas",
        "Extract numeric value + units",
        "Convert units to SI",
        "Clear duplicate rows",
        "Move rows or columns",
        "Plot data",
        "Generate LaTeX table"
    ]

    while True:
        print("\n==============================")
        print("Available actions:")
        print("==============================")

        for i, action in enumerate(actions, 1):
            print(f"{i}) {action}")

        print("\nCommands:")
        print("  numbers separated by space  -> select actions")
        print("  quit                        -> cancel")

        # user input like: 1 3 5
        raw = input("\nChoose actions: ").strip().lower()

        if raw == "quit":
            return None

        # split input into tokens
        tokens = raw.split()
        if not all(t.isdigit() for t in tokens):
            print("Please enter valid numbers.")
            continue

        nums = list(map(int, tokens))
        if not all(1 <= n <= len(actions) for n in nums):
            print("Some numbers were invalid.")
            continue

        # Deduplicate & map numbers to action names
        selected = [actions[n - 1] for n in dict.fromkeys(nums)]

        print("\nYou have chosen to perform:")
        for act in selected:
            print(" -", act)

        while True:
            confirm = input("\nAre you sure? (y/n): ").strip().lower()
            if confirm in ("y", "yes"):
                return selected
            elif confirm in ("n", "no"):
                print("\nOkay, let's choose again.")
                break
            else:
                print("Please type y or n.")
                
def choose_output_path() -> str:
   
    print("\n==============================")
    print("Saving cleaned CSV")
    print("==============================")
    print("Project directory:", Root_dir)

    print("\nEnter output file path relative to the working directory.")
    print("Examples:")
    print("   cleaned.csv")
    print("   Cleaned_csv/Cleaned.csv")
    print("   output/run1/cleaned.csv\n")

    while True:
        out = input("Output file path: ").strip()

        if not out.lower().endswith(".csv"):
            print("Output must end with .csv")
            continue

        # Save relative to the project folder
        output_path = os.path.join(Root_dir, out)

        # Make folder(s) if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        return output_path
    
# Helper to read messy
def load_csv_loose(csv_path: str) -> pd.DataFrame:
    """
    Tries to read CSV normally.
    If it fails with ParserError, retries with relaxed options
    and skips bad lines.
    """
    try:
        return pd.read_csv(
            csv_path,
            encoding="utf-8",
            keep_default_na=False,   # <── add this
        )
    except ParserError as e:
        print("\nParserError while reading CSV:")
        print(e)
        print("\nRetrying with relaxed settings (engine='python', on_bad_lines='skip')...\n")
        return pd.read_csv(
            csv_path,
            engine="python",
            on_bad_lines="skip",
            keep_default_na=False,   # <── add this
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            csv_path,
            encoding="latin1",
            encoding_errors="ignore",
            keep_default_na=False,   # <── add this
        )

def main():
    csv_path = browse_and_choose_csv()
    if csv_path is None:
        print("\nNo CSV selected.")
        return

    file = load_csv_loose(csv_path)

    chosen_actions = choose_csv_actions()
    if chosen_actions is None:
        print("No actions selected.")
        return

    # ---------------------------------
    # Decide if any chosen actions modify the CSV
    # ---------------------------------
    mutating_actions = [
        a for a in chosen_actions
        if a not in ("Plot data", "Generate LaTeX table")
    ]

    if mutating_actions:
        # Ask if the user wants a cleaning log (ONLY if something can change the CSV)
        while True:
            ans = input(
                "\nGenerate cleaning log (.txt) next to cleaned CSV? (y/n): "
            ).strip().lower()
            if ans in ("y", "yes"):
                log_enabled = True
                break
            elif ans in ("n", "no"):
                log_enabled = False
                break
            else:
                print("Please type y or n.")

        log_entries = []
        if log_enabled:
            log_entries.append(f"Source file: {csv_path}")
            log_entries.append(
                f"Initial shape: {file.shape[0]} rows x {file.shape[1]} columns"
            )
            log_entries.append("")
    else:
        # ONLY Plot data / Generate LaTeX chosen → no cleaning log at all
        log_enabled = False
        log_entries = []
    # ---------------------------------

    # ----------------------------
    # Importing actions
    # ----------------------------
    for action in chosen_actions:
        before_df = file.copy(deep=True)

        if action == "Remove rows and columns":
            from csv_actions import remove_rows_and_columns
            file = remove_rows_and_columns(file)
        if action == "Strip whitespace":
            from csv_actions import strip_whitespace
            file = strip_whitespace(file)
        if action == "Normalize missing values":
            from csv_actions import normalize_missing_values
            file = normalize_missing_values(file)
        if action == "Fix decimal commas":
            from csv_actions import fix_decimal_commas
            file = fix_decimal_commas(file)
        if action == "Extract numeric value + units":
            from csv_actions import extract_numeric_and_unit
            file = extract_numeric_and_unit(file)
        if action == "Convert units to SI":
            from csv_actions import convert_units_to_SI
            file = convert_units_to_SI(file)
        if action == "Clear duplicate rows":
            from csv_actions import remove_duplicate_rows
            file = remove_duplicate_rows(file)
        if action == "Move rows or columns":
            from csv_actions import move_rows_or_columns
            file = move_rows_or_columns(file)
        if action == "Plot data":
            from csv_actions import plot_data
            file = plot_data(file, file_path=csv_path)
        if action == "Generate LaTeX table":
            from csv_actions import generate_latex_table
            file = generate_latex_table(file)

        if log_enabled:
            _update_cleaning_log(action, before_df, file, log_entries)
    # ----------------------------

    save_needed = any(a not in ("Plot data", "Generate LaTeX table") for a in chosen_actions)

    if save_needed:
        output_path = choose_output_path()
        file.to_csv(output_path, index=False)
        print(f"\nSaved cleaned file as:\n{output_path}")

        if log_enabled:
            base, _ = os.path.splitext(output_path)
            log_path = base + "_log.txt"
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(log_entries))
            print(f"\nCleaning log saved as:\n{log_path}")
    else:
        print("\nOnly plotting/LaTeX was performed. CSV not saved.")

# Needed for the program to run when executed directly and not when imported
if __name__ == "__main__":
    main()