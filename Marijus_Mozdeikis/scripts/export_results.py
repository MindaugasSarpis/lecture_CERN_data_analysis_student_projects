import pandas as pd
import os

def export_peak_results(filename, results, output_file="resonance_properties.xlsx", 
                       sheet_name="All_Results", start_row=None):
    """Export results starting at specific Excel row."""
    
    sheet_name = "All_Results"
    df_new = pd.DataFrame(results)
    
    # Ensure file/column columns exist
    if "file" not in df_new.columns:
        df_new["file"] = filename
    
    # Reorder columns
    desired_order = ["file", "column", "resonance_order", "peak_wl", "depth", "fwhm", "Q", "MQ"]
    existing_cols = [col for col in desired_order if col in df_new.columns]
    other_cols = [col for col in df_new.columns if col not in existing_cols]
    df_new = df_new[existing_cols + other_cols]
    
    file_exists = os.path.exists(output_file)
    
    # Convert Excel row to pandas index (subtract 2: Excel row 12 → pandas row 10)
    if start_row is not None:
        pandas_start_row = max(0, start_row - 2)  # ← KEY CHANGE!
        excel_row = start_row
    else:
        pandas_start_row = None
        excel_row = None
    
    if pandas_start_row is not None:
        if file_exists:
            try:
                existing_df = pd.read_excel(output_file, sheet_name=sheet_name)
                
                # If starting beyond existing data, add empty rows
                if pandas_start_row > len(existing_df):
                    empty_rows = pandas_start_row - len(existing_df)
                    empty_df = pd.DataFrame([[""] * len(existing_df.columns)] * empty_rows, 
                                           columns=existing_df.columns)
                    existing_df = pd.concat([existing_df, empty_df], ignore_index=True)
                    print(f"  📏 Added {empty_rows} empty rows")
                
                # Insert new data
                for i in range(len(df_new)):
                    if pandas_start_row + i < len(existing_df):
                        existing_df.iloc[pandas_start_row + i] = df_new.iloc[i]
                    else:
                        existing_df = pd.concat([existing_df, df_new.iloc[[i]]], ignore_index=True)
                
                final_df = existing_df
                print(f"  📝 Inserted at Excel row {excel_row}")
                
            except Exception as e:
                print(f"  ⚠ Error: {e}, appending instead")
                final_df = pd.concat([existing_df, df_new], ignore_index=True)
        else:
            # Create new file with empty rows at the top
            if pandas_start_row > 0:
                empty_df = pd.DataFrame([[""] * len(df_new.columns)] * pandas_start_row, 
                                       columns=df_new.columns)
                final_df = pd.concat([empty_df, df_new], ignore_index=True)
                print(f"  📄 Created new file, data starts at Excel row {excel_row}")
            else:
                final_df = df_new
                print(f"  📄 Created new file, data starts at Excel row 2")
    
    else:
        # AUTO-APPEND
        if file_exists:
            try:
                existing_df = pd.read_excel(output_file, sheet_name=sheet_name)
                final_df = pd.concat([existing_df, df_new], ignore_index=True)
                print(f"  ➕ Appended {len(df_new)} rows")
            except:
                final_df = df_new
        else:
            final_df = df_new
    
    # Write to Excel
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        final_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"  💾 Saved to: {output_file}")