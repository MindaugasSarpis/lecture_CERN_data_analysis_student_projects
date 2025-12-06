import pandas as pd
import os
import numpy as np

def load_signal(folder, filename, column_suffix, multiple=False):
    """Load wavelength array and inverted signal from an Excel file."""

    # Locate file
    file_path = os.path.join(folder, filename)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Load Excel sheet
    df = pd.read_excel(file_path, sheet_name="Calibration 1-Measurements")

    # Identify relevant columns
    wavelengths = pd.to_numeric(df[df.columns[0]], errors="coerce").values

    p_cols = [col for col in df.columns if col.endswith(column_suffix)]
    if not p_cols:
        raise ValueError(f"No columns ending with '{column_suffix}' found")

    # Process and invert signals
    signals = {}
    for col in p_cols:
        raw = pd.to_numeric(df[col], errors="coerce").values
        inv = np.nanmax(raw) - raw
        signals[col] = inv

    if multiple:
        return {col: (wavelengths, df[col].max() - df[col].values) for col in p_cols}
    return wavelengths, signal

