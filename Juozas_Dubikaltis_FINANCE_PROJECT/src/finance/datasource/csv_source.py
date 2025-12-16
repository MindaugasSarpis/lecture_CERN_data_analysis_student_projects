from pathlib import Path
import pandas as pd

def _smart_read_csv(p: Path) -> pd.DataFrame:
    # Try UTF-8 with automatic delimiter detection
    try:
        df = pd.read_csv(p, sep=None, engine="python", encoding="utf-8-sig", on_bad_lines="skip")
        if df.shape[1] == 1:  # probably wrong delimiter
            raise ValueError("single column, retry with ;")
        return df
    except Exception:
        pass
    # Try semicolon + comma-decimal (common for banks)
    try:
        df = pd.read_csv(p, sep=";", encoding="utf-8-sig", decimal=",", on_bad_lines="skip")
        return df
    except Exception:
        pass
    # Last resort legacy encoding
    return pd.read_csv(p, sep=";", encoding="latin1", decimal=",", on_bad_lines="skip")

class CsvSource:
    def __init__(self, paths: list[Path]):
        self.paths = paths

    def fetch(self) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for p in self.paths:
            df = _smart_read_csv(p)
            df["_source_path"] = str(p)
            frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)
