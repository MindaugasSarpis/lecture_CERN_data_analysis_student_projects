import pandas as pd
from pathlib import Path

URL = "http://opendata.cern.ch/record/545/files/Dimuon_DoubleMu.csv"

def load_dimuon_csv(path: str | Path | None = None) -> pd.DataFrame:
    if path is None:
        return pd.read_csv(URL)
    path = Path(path)
    return pd.read_csv(path)