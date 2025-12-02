from data_tools import load_signal
from plot_tools import plot_with_sliders_and_baseline
from export_results import export_peak_results
from peak_tools import analyze_signal_with_custom_baseline
import os

# ---------------- CONFIGURATION ----------------
folder = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\20250722_05nJ_06-10um_Spectras"
filename = "20250722_05nJ_09um.xlsx"
column_suffixes = [" P ", " S "]
initial_prominence = 10
initial_distance = 10
output_file = r"C:\Users\Marijus\OneDrive - Vilnius University\3 semestras\cern\Marijus\Marijus_Mozdeikis\results\resonance_properties.xlsx"
# ------------------------------------------------
start_row = 16  # Excel row to start inserting results
print(f"📊 Processing: {filename}")
print(f"📁 Output: {output_file}")
print(f"📍 Will insert at row {start_row} (Excel row {start_row})")

resonance_properties = []

for suffix in column_suffixes:
    signals = load_signal(folder, filename, suffix, multiple=True)
    
    for col_name, (wavelengths, signal) in signals.items():
        print(f"\n  📋 Column: {col_name}")
        
        final_values = plot_with_sliders_and_baseline(
            wavelengths, signal, 
            initial_prominence, initial_distance, 
            title=f"{filename}: {col_name}"
        )
        
        results = analyze_signal_with_custom_baseline(
            wavelengths, signal, col_name, 
            final_values['prominence'], 
            final_values['distance'], 
            final_values['baselines']['left_bases']
        )
        
        for r in results:
            r["file"] = filename
            r["column"] = col_name
            resonance_properties.append(r)
        
        print(f"    ✅ Found {len(results)} resonance(s)")

# Export at SPECIFIED row
if resonance_properties:
    export_peak_results(filename, resonance_properties, 
                       output_file=output_file, 
                       start_row=start_row)  # ← HERE
    
    print(f"\n✅ DONE!")
    print(f"   File: {filename}")
    print(f"   Rows: {len(resonance_properties)}")
    print(f"   Location: Excel rows {start_row} to {start_row + len(resonance_properties)}")
else:
    print("\n⚠ No results to save")