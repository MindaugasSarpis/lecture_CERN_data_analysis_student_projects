from data_tools import load_signal
from plot_tools import plot
from export_results import export_peak_results
from peak_tools import analyze_signal
import os

# CONFIGURATION
folder = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\20250722_05nJ_06-10um_Spectras"
filename = "20250722_05nJ_09um.xlsx"
column_suffixes = [" P ", " S "]
initial_prominence = 10
initial_distance = 10
output_file = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\results\resonanc.xlsx"
sheet_name = "Allll"
start_row = 14

print(f"Processing: {filename}")

resonance_properties = []

# Process each specified column suffix
for suffix in column_suffixes:
    signals = load_signal(folder, filename, suffix, multiple=True)
    
    for col_name, (wavelengths, signal) in signals.items():
        print(f"Column: {col_name}")
        
        final_values = plot(wavelengths, signal, initial_prominence, initial_distance, 
            title=f"{filename}: {col_name}")
        
        results = analyze_signal(wavelengths, signal, col_name, final_values['prominence'], 
            final_values['distance'], final_values['baselines']['left_bases'])
        
        for r in results:
            r["file"] = filename
            r["column"] = col_name
            resonance_properties.append(r)

# Export at specified row
if resonance_properties:
    export_peak_results(filename, resonance_properties, output_file, sheet_name, start_row)
    
    print(f"---DONE!---")
    print(f" Saved to: {output_file}")
    print(f" Location: Excel rows {start_row} to {start_row + len(resonance_properties)-1}")
else:
    print("\n⚠ No results to save")