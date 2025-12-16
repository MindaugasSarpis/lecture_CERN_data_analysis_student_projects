#!/usr/bin/env python3
"""
fix_csv.py



#! To run file in terminal write:

#! fix_csv.py Data.ex2.csv --group-by-header --replace-literal-tabs --inplace
#! fix_csv.py File_Name --group-by-header --replace-literal-tabs --inplace




Helper to convert space/tab-separated or mixed-separator data files into proper comma-separated CSVs.

Usage examples:
  python fix_csv.py Data.ex3.csv
  python fix_csv.py Data.ex3.csv -o Data.ex3_comma.csv --method pandas
  python fix_csv.py Data.ex3.csv --inplace --force

Features:
- Makes a backup by default (input.bak)
- Can replace literal "\\t" sequences with real tabs
- Two conversion methods: "regex" (fast, simple) and "pandas" (robust, handles quotes)
- Preview output (first 5 lines / rows)
- Optional inplace replace of the original file (with confirmation)
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path
import sys
import re
from io import StringIO

try:
    import pandas as pd
except Exception:
    pd = None


def parse_args():
    p = argparse.ArgumentParser(description="Convert mixed/space-delimited data to comma-separated CSV.")
    p.add_argument("input", help="Input data file")
    p.add_argument("-o", "--output", help="Output CSV file (default: <input>_comma.csv)")
    p.add_argument("--method", choices=["regex", "pandas"], default="regex",
                   help="Conversion method: regex (fast) or pandas (robust)")
    p.add_argument("--no-backup", dest="backup", action="store_false", help="Don't create a .bak backup")
    p.add_argument("--replace-literal-tabs", action="store_true",
                   help="Replace literal \\t sequences (two characters) with real tabs before parsing")
    p.add_argument("--group-by-header", action="store_true",
                   help="Treat the first non-empty line as a header and group subsequent tokens into rows matching header column count")
    p.add_argument("--group-size", type=int, default=0,
                   help="Force grouping of tokens into rows of this size (overrides --group-by-header if >0)")
    p.add_argument("--inplace", action="store_true", help="Replace the original file with the converted CSV (asks before overwriting)")
    p.add_argument("--force", action="store_true", help="When used with --inplace, don't ask for confirmation")
    p.add_argument("--preview-rows", type=int, default=5, help="Number of rows/lines to show as preview")
    return p.parse_args()


def backup_file(path: Path):
    # Create a BackUps folder next to the input file and store backups there
    backups_dir = path.parent / "BackUps"
    backups_dir.mkdir(parents=True, exist_ok=True)

    bak = backups_dir / (path.name + ".bak")
    if bak.exists():
        print(f"Backup already exists: {bak}")
        return bak

    shutil.copy2(path, bak)
    print(f"Backup created: {bak}")
    return bak


def convert_regex(raw: str) -> str:
    # First, collapse any combination of spaces/tabs into a single comma
    # But keep quoted fields intact is hard with simple regex; this is a best-effort
    # Replace runs of whitespace with a single comma
    out = re.sub(r"\s+", ", ", raw)
    return out


def convert_pandas(raw: str) -> tuple[str, object]:
    if pd is None:
        raise RuntimeError("pandas is required for the 'pandas' method. Install with: pip install pandas")
    sio = StringIO(raw)
    # Try inference first
    try:
        df = pd.read_csv(sio, sep=None, engine='python')
        return df.to_csv(index=False), df
    except Exception:
        sio.seek(0)
    try:
        df = pd.read_csv(StringIO(raw), sep=r"\s+", engine='python')
        return df.to_csv(index=False), df
    except Exception as e:
        raise RuntimeError(f"pandas parsing failed: {e}")


def main():
    args = parse_args()
    inp = Path(args.input)
    if not inp.exists():
        print(f"Input file not found: {inp}")
        sys.exit(2)

    # Prepare output path. If no explicit output is given, place converted files
    # into a `Seperated` folder next to the input file.
    if args.output:
        out = Path(args.output)
    else:
        separated_dir = inp.parent / "Seperated"
        separated_dir.mkdir(parents=True, exist_ok=True)
        out = separated_dir / (inp.stem + "_comma" + inp.suffix)

    if args.backup:
        backup_file(inp)

    raw = inp.read_text(encoding='utf-8', errors='replace')

    if args.replace_literal_tabs:
        if "\\t" in raw:
            raw = raw.replace("\\t", "\t")
            print("Replaced literal \\t with actual tabs before parsing")

    # Optional grouping mode: group tokens into rows based on header or provided size.
    # If not explicitly requested, auto-detect header grouping when the first
    # non-empty line looks like a header (non-numeric tokens) and subsequent
    # data lines don't match the header token count.
    auto_group = False
    if not args.group_by_header and args.group_size == 0:
        # detect header-like first line
        lines_all = [ln for ln in raw.splitlines() if ln.strip() != ""]
        if len(lines_all) >= 2:
            first = lines_all[0].strip()
            # header tokens (split on comma or whitespace)
            hdr_tokens = [t.strip() for t in (first.split(",") if "," in first else re.split(r"\s+", first)) if t.strip()]
            # If header tokens contain any non-numeric strings (letters), consider it a header
            has_text = any(re.search(r"[A-Za-z]", t) for t in hdr_tokens)
            if has_text:
                # check token counts of next few lines
                mismatch = 0
                check_lines = lines_all[1: min(len(lines_all), 20)]
                for ln in check_lines:
                    tokens = re.findall(r"\S+", ln)
                    if len(tokens) != len(hdr_tokens):
                        mismatch += 1
                # if there are mismatches, auto group
                if mismatch > 0:
                    auto_group = True

    if args.group_by_header or args.group_size > 0 or auto_group:
        lines = [ln for ln in raw.splitlines() if ln.strip() != ""]
        if not lines:
            print("No content to group after stripping blank lines.")
            sys.exit(2)

        if args.group_size > 0:
            group_size = args.group_size
            header_tokens = None
            data_lines = lines
        else:
            # group by header: first non-empty line is header
            header_line = lines[0]
            # detect header separator
            if "," in header_line:
                header_tokens = [t.strip() for t in header_line.split(", ") if t.strip()]
            else:
                header_tokens = re.split(r"\s+", header_line.strip())
            group_size = len(header_tokens)
            data_lines = lines[1:]

        # Tokenize remaining data by non-whitespace sequences
        tokens = re.findall(r"\S+", "\n".join(data_lines))
        if not tokens:
            print("No data tokens found to group.")
            sys.exit(2)

        # Pad tokens if necessary
        pad = (-len(tokens)) % group_size
        if pad:
            tokens.extend([""] * pad)

        rows = [tokens[i : i + group_size] for i in range(0, len(tokens), group_size)]

        if header_tokens is None:
            header_tokens = [f"col{i+1}" for i in range(group_size)]

        csv_lines = [", ".join(header_tokens)] + [", ".join(row) for row in rows]
        out_text = "\n".join(csv_lines) + "\n"
        out.write_text(out_text, encoding="utf-8")
        print(f"Written grouped CSV to: {out}")

        # If pandas available, show a dataframe preview
        if pd is not None:
            df = pd.read_csv(StringIO(out_text))
            print(df.head(args.preview_rows).to_string(index=False))
        else:
            with out.open("r", encoding="utf-8") as fh:
                for i in range(args.preview_rows):
                    line = fh.readline()
                    if not line:
                        break
                    print(line.rstrip("\n"))

    else:
        if args.method == "regex":
            out_text = convert_regex(raw)
            # Ensure newline termination
            if not out_text.endswith("\n"):
                out_text += "\n"
            out.write_text(out_text, encoding='utf-8')
            print(f"Written converted file (regex) to: {out}")
            # Print preview lines
            with out.open('r', encoding='utf-8') as fh:
                for i in range(args.preview_rows):
                    line = fh.readline()
                    if not line:
                        break
                    print(line.rstrip('\n'))
            df = None
        else:
            # pandas method
            csv_text, df = convert_pandas(raw)
            out.write_text(csv_text, encoding='utf-8')
            print(f"Written converted file (pandas) to: {out}")
            # Show df preview
            print(df.head(args.preview_rows).to_string(index=False))

    if args.inplace:
        if not args.force:
            ans = input(f"Overwrite original file {inp} with {out}? (Y/N): ").strip().lower()
            if ans not in ('y', 'yes'):
                print("Mission aborted")
                return
        # Overwrite original
        shutil.copy2(out, inp)
        print(f"Original file {inp} replaced with converted CSV")

    print("Done.")


if __name__ == '__main__':
    main()
