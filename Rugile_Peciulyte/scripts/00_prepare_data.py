import os
import zipfile
import shutil

RAW_ZIP_PATH = "data/raw/superconductivity.zip"
PROCESSED_DIR = "data/processed"
RAW_TRAIN_NAME = "train.csv"
PROCESSED_CSV = os.path.join(PROCESSED_DIR, "train_engineered.csv")

def main():
    if os.path.exists(PROCESSED_CSV):
        print(f"[INFO] Processed CSV already exists at {PROCESSED_CSV}. Nothing to do.")
        return

    if not os.path.exists(RAW_ZIP_PATH):
        raise FileNotFoundError(f"Raw dataset not found at {RAW_ZIP_PATH}.")

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    with zipfile.ZipFile(RAW_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall("data/raw")
        print(f"[INFO] Extracted {RAW_ZIP_PATH} to {PROCESSED_DIR}")
    
    src_path = os.path.join("data/raw", RAW_TRAIN_NAME)

    if not os.path.exists(src_path):
        raise FileNotFoundError(f"{RAW_TRAIN_NAME} not found after extraction")
    
    shutil.copy(src_path, PROCESSED_CSV)
    print(f"[INFO] Copied {src_path} -> {PROCESSED_CSV}")
    
    print("[INFO] Data preparation complete.")

if __name__ == "__main__":
    main()
