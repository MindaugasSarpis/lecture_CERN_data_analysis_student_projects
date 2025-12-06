import pandas as pd
import os

def export_peak_results(filename, results, output_file, sheet_name, start_row=None):
    """Export results starting at specific Excel row."""
    
    df_new = pd.DataFrame(results)
    
    # Ensure file/columns exist
    if "file" not in df_new.columns:
        df_new["file"] = filename
    
    # Reorder columns
    desired_order = ["file", "column", "resonance_order", "peak_wl", "depth", "fwhm", "Q", "MQ",]
    df_new = df_new[desired_order]
    
    # Convert Excel row to pandas index
    if start_row is not None:
        pandas_start_row = max(0, start_row - 2)
    else:
        pandas_start_row = None

    # Check if file exists
    file_exists = os.path.exists(output_file)
    
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
                
            except Exception as e:
                print(f" Error reading existing file: {e}")
                print(f"  Creating new file instead")
                # If can't read, create new
                if pandas_start_row > 0:
                    empty_df = pd.DataFrame([[""] * len(df_new.columns)] * pandas_start_row, columns=df_new.columns)
                    final_df = pd.concat([empty_df, df_new], ignore_index=True)
                else:
                    final_df = df_new
        else:
            # Create new file with empty rows at the top
            if pandas_start_row > 0:
                empty_df = pd.DataFrame([[""] * len(df_new.columns)] * pandas_start_row, 
                                       columns=df_new.columns)
                final_df = pd.concat([empty_df, df_new], ignore_index=True)
            else:
                final_df = df_new
    
    else:
        # AUTO-APPEND
        if file_exists:
            try:
                existing_df = pd.read_excel(output_file, sheet_name)
                final_df = pd.concat([existing_df, df_new], ignore_index=True)
            except Exception as e:
                print(f" Error reading file, creating new: {e}")
                final_df = df_new
        else:
            final_df = df_new
    
    # Write to Excel
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        final_df.to_excel(writer, sheet_name=sheet_name, index=False)