from data_tools import load_signal
from plot_tools import plot_with_sliders
from export_results import export_peak_results
from peak_tools import analyze_signal

# ---------------- CONFIGURATION ----------------
folder = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\20250722_05nJ_06-10um_Spectras"
filename = "20250722_05nJ_08um.xlsx"
column_suffixes = [" P ", " S "]
initial_prominence = 4
initial_distance = 10
output_file = "resonance_properties.xlsx"
# ------------------------------------------------

resonance_properties = []

for suffix in column_suffixes:
    signals = load_signal(folder, filename, suffix, multiple=True)

    for col_name, (wavelengths, signal) in signals.items():
        print(f"\n=== Processing column: {col_name} ===")
        plot_with_sliders(wavelengths, signal, initial_prominence, initial_distance, title=col_name)
        results = analyze_signal(wavelengths, signal, initial_prominence, initial_distance)
        for r in results:
            r["file"] = filename
            r["column"] = col_name
            resonance_properties.append(r)

export_peak_results(filename, resonance_properties, output_file=output_file)