# CMS Dimuon Spectrum (CERN Open Data)
---

This project analyses the invariant mass spectrum of dimuon events from the CMS experiment at the LHC using publicly available open data from CERN.

## 1. Dataset

We use the CMS education/outreach dataset:

> **Events with two muons from 2011 (Primary dataset DoubleMu 2011A)**  
> CMS Open Data, 100 000 events with two reconstructed muons. 

Key features:

- Proton–proton collisions at $\sqrt{s}=7$ TeV recorded in 2011.
- Exactly **two muon candidates** per event.
- Kinematic and charge information for each muon:
  - energy $E$, momentum components $p_x,\;p_y,\;p_z$,
  - transverse momentum $p_T$,
  - pseudorapidity $\eta$,
  - azimuthal angle $\phi$,
  - charge $Q$.
- The CSV also contains the pre-computed dimuon invariant mass $M$ [GeV].

The data are provided via the CERN Open Data Portal in CSV format and are intended for **education and outreach**, not for precision physics measurements.

### 1.1 Downloading the CSV

By default, the analysis code **streams** the CSV directly from CERN using the URL


http://opendata.cern.ch/record/545/files/Dimuon_DoubleMu.csv

---

# 2. Code Components Documentation

The project follows a **modular layout**:

- `data_io.py` – data loading only
- `physics.py` – physics/analysis logic (no plotting)
- `fit.py` – fitting models and numerical optimisation
- `plots.py` – all visualisation
- `main.py` – orchestration / entry point

This separation is intentional: it keeps I/O, physics, plotting, and control flow decoupled.

---

## 2.1 `data_io.py`

**Purpose:** `data_io.py` contains all the logic needed to **load the dimuon dataset**. It isolates external data handling from the rest of the analysis.

### Functions

#### `load_dimuon_csv(path: str | Path | None = None) -> pd.DataFrame`

Loads the CMS dimuon CSV data into a `pandas.DataFrame`.

- **Parameters**
  - `path` (optional):  
    - `None`: load directly from the official CERN Open Data URL.  
    - `str` or `Path`: interpret as a local file path and load from disk.

- **Returns**
  - `pd.DataFrame` with one row per event and columns:
    - event metadata (run, event ID, etc. – depending on the CSV),
    - kinematic variables of the two muons (`E1`, `px1`, `py1`, `pz1`, `pt1`, `eta1`, `phi1`, `Q1`, and same for `2`),
    - invariant mass `M` in GeV.

### Design notes

- No physics or plotting logic is allowed here.
- The rest of the code depends only on the **DataFrame interface**, not on how or from where it is loaded.

---

## 2.2 `physics.py`

**Purpose:** `physics.py` contains the **core analysis logic** that operates on numerical arrays / DataFrames but does not produce any plots. It is the “physics engine” of the project.

### Functions

#### `compute_invariant_mass(df: pd.DataFrame) -> np.ndarray`

Recomputes the dimuon invariant mass from four-vectors:

- Reads `E1`, `E2`, `px1`, `px2`, `py1`, `py2`, `pz1`, `pz2` from the DataFrame.
- Forms summed four-vector:
  $
  E = E_1 + E_2,\quad
  p_x = p_{x1} + p_{x2},\quad
  p_y = p_{y1} + p_{y2},\quad
  p_z = p_{z1} + p_{z2}.
  $
- Computes
  $
  m_{\mu\mu}^2 = E^2 - (p_x^2 + p_y^2 + p_z^2)
  $
  and returns $\sqrt{\max(m^2, 0)}$ to avoid numerical issues.

**Returns**: `np.ndarray` of masses [GeV], one value per event.


#### `count_in_window(masses: np.ndarray, m_min: float, m_max: float) -> int`

Counts events in a fixed invariant mass window.

- **Parameters**
  - `masses`: 1D array of invariant masses.
  - `m_min`, `m_max`: lower and upper bounds of the window (GeV).

- **Returns**
  - Integer count of events with `m_min ≤ m < m_max`.


#### `print_yields(masses: np.ndarray) -> None`

Prints the event yields in a set of predefined mass windows corresponding to main resonance regions:

- $J/\psi$ region (around 3 GeV),
- $\psi(2S)$ region,
- $\Upsilon$ region (9–10 GeV),
- $Z$ region (80–100 GeV).

Uses `count_in_window` internally and writes human-readable output like:


> $J/\psi$ region  :  N events in [2.8, 3.3] GeV

> $Z$ region       :  N events in [80.0, 100.0] GeV

---

### 2.3 `fit.py`

**Purpose:** all fitting logic; currently just a simple Gaussian model and a Z peak fit.

**Functions:**

- `gaussian(x, A, mu, sigma)`  
  Gaussian model for histogram fitting:
  $
  g(x; A, \mu, \sigma) = A \exp\left[-\tfrac{1}{2} \left(\frac{x - \mu}{\sigma}\right)^2 \right].
  $

- `fit_z_peak(masses, m_min: float = 80.0, m_max: float = 100.0, nbins: int = 120)` '
  - Restricts `masses` to the Z region `[m_min, m_max]` (default 80–100 GeV).  
  - Builds a histogram with 'nbins' bins.  
  - Computes bin centres.  
  - Uses `scipy.optimize.curve_fit` with `gaussian` to fit the histogram.  

  **Returns:**
  - `centers`: bin centres,
  - `counts`: bin heights,
  - `popt`: best-fit parameters `(A, mu, sigma)`,
  - `pcov`: covariance matrix of the fit.

`fit.py` is purely numerical; it doesn’t produce any plots itself.

---

### 2.4 `plots.py`

**Purpose:** Visualises the data and applies the fits. Uses matplotlib + SciencePlots styles.

SCiencePlots (https://github.com/garrettj403/SciencePlots) package has been used to for nicer data Visualization styles:

>plt.style.use(["science", "notebook", "grid"])

---

### 2.5 `main.py`

**Purpose:** Performs the full analysis. Orchestrates the full pipeline by calling functions from the other modules in a well–defined order.

### How to run

- Choose the parameters and save the file,
- In the terminal find the location of the file,
- Using `python3 main.py` run the program,
- Enjoy the results!
