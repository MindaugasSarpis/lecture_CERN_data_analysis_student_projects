import pandas as pd
import sys
import os

def read_from_link(link):
    """
    Read CSV data from a Google Drive link
    """
    try:
        file_id = None
        
        # Format 1: https://drive.google.com/file/d/FILE_ID/view
        if '/file/d/' in link:
            parts = link.split('/file/d/')[1].split('/')
            file_id = parts[0]
        
        # Format 2: https://drive.google.com/open?id=FILE_ID
        elif 'id=' in link:
            file_id = link.split('id=')[1].split('&')[0]
        
        # Format 3: Direct ID 
        else:
            file_id = link
        
        if not file_id:
            raise ValueError(f"Could not extract file ID from: {link}")
        
        # Create direct download URL
        download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
        
        # Download and read CSV
        print(f"Downloading from Google Drive...")
        df = pd.read_csv(download_url)
        return df
        
    except Exception as e:
        print(f"Error reading from link: {e}")
        return None

def read_from_file(filepath):
    """
    Read CSV data from a local file
    """
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            return None
        
        # Read CSV file
        df = pd.read_csv(filepath)
        return df
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
def main():
    """
    Main function to handle command line arguments
    """

    if len(sys.argv) < 3:
        print("Usage:")
        print("  To read from Google Drive link: python extract_data.py 1 <link>")
        print("  To read from local file:        python extract_data.py 2 <filename>")
        print("\nExamples:")
        print("  python extract_data.py 1 https://drive.google.com/file/d/YOUR_FILE_ID/view")
        print("  python extract_data.py 2 data/neo_data.csv")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    source = sys.argv[2]
    
    if mode == '1':
        data = read_from_link(source)
    elif mode == '2':
        data = read_from_file(source)
    else:
        print(f"Error: First argument must be 1 or 2, not '{mode}'")
        sys.exit(1)
    
    if data is not None:
        print(f"\n✓ Data loaded successfully!")
        print(f"  Records: {len(data)}")
        print(f"  Columns: {len(data.columns)}")

if __name__ == "__main__":
    main()