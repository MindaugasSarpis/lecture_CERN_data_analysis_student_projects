import numpy as np
import pandas as pd

def compute_invariant_mass(df: pd.DataFrame) -> np.ndarray:
    #Four-vector component construction
    E1, E2   = df["E1"], df["E2"]
    px1, px2 = df["px1"], df["px2"]
    py1, py2 = df["py1"], df["py2"]
    pz1, pz2 = df["pz1"], df["pz2"]

    E  = E1 + E2
    px = px1 + px2
    py = py1 + py2
    pz = pz1 + pz2

    #Calculating the invariant mass
    m2 = E**2 - (px**2 + py**2 + pz**2)
    return np.sqrt(np.maximum(m2, 0.0))

def count_in_window(masses: np.ndarray, m_min: float, m_max: float) -> int:
    # Counts how man masses fall inside a window
    mask = (masses >= m_min) & (masses < m_max)
    return int(mask.sum())

#Function for printing yields
def print_yields(masses: np.ndarray) -> None:
    windows = {
        "J/psi region"   : (2.8, 3.3),
        "psi(2S) region" : (3.4, 3.8),
        "Upsilon region" : (9.0, 10.0),
        "Z region"       : (80.0, 100.0),
    }
    for name, (a, b) in windows.items():
        n = count_in_window(masses, a, b)
        print(f"{name:15s}: {n:6d} events in [{a}, {b}] GeV")
