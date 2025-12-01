import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import re
import sys

#if in One-Drive
sys.path.append(r"C:\Users\Marijus\miniconda3\envs\Spectra\Lib\site-packages")

# Folder path
folder = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\20250722_05nJ_06-10um_Spectras"
output_folder = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\results"
files = glob.glob(os.path.join(folder, "*.xlsx"))

# Function to extract angle from column name
def get_angle(col):
    match = re.search(r'R (\d+)', col)
    if match:
        return match.group(1) + "°"
    else:
        return col

# Function to extract period from filename
def get_period(f):
    match = re.search(r'_(\d+)um', os.path.basename(f))
    if match:
        period_num = int(match.group(1)) / 10
        return f"{period_num} μm"
    else:
        return "Unknown Period"

# Read the Excel file and plot the data
for f in files:
    print(f"Working with: {os.path.basename(f)}")
    period = get_period(f)
    df = pd.read_excel(f, sheet_name="Calibration 1-Measurements")
    wavelength_col = df.columns[0]
    s_cols = [c for c in df.columns if c.endswith(" S ")]
    p_cols = [c for c in df.columns if c.endswith(" P ")]
    base_name = os.path.splitext(os.path.basename(f))[0]

    # Plot S polarization
    plt.figure(figsize=(10, 5))
    for col in s_cols:
        plt.plot(df[wavelength_col], df[col], label = get_angle(col))
    # Design the plot
    plt.legend()
    plt.title(f"S polarization: {period}, 0.5 nJ, Ag 50 nm ITO")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflection (%)")
    plt.grid()
    plt.savefig(os.path.join(output_folder, f"{base_name}_S.png"))
    plt.close()

    # Plot P polarization
    plt.figure(figsize=(10, 5))
    for col in p_cols:
        plt.plot(df[wavelength_col], df[col], label = get_angle(col))
    # Design the plot
    plt.legend()
    plt.title(f"P polarization: {period}, 0.5 nJ, Ag 50 nm ITO")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Reflection (%)")
    plt.grid()
    plt.savefig(os.path.join(output_folder, f"{base_name}_P.png"))
    plt.close()