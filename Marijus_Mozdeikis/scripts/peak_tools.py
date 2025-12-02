from scipy.signal import find_peaks
import numpy as np

def detect_peaks(signal, prominence, distance):
    # Return peak indices + peak properties
    return find_peaks(signal, prominence=prominence, distance=distance)

def calculate_depths(signal, peaks, properties):
    # Compute depth = baseline - peak value using left_bases
    depths = []
    left_bases = properties["left_bases"]

    for p, lb in zip(peaks, left_bases):
        baseline = signal[lb]
        peak_val = signal[p]

        depths.append({
            "peak_index": p,
            "baseline_index": lb,
            "baseline_value": baseline,
            "peak_value": peak_val,
            "depth": baseline - peak_val
        })

    return depths

def calculate_fwhm(signal, wavelengths, peaks, left_bases):
    """Calculate FWHM with interpolation (closer to Origin's method)."""
    fwhms = []
    
    for p, lb in zip(peaks, left_bases):
        baseline = signal[lb]
        dip = signal[p]
        
        # Calculate half-maximum for a DIP
        half_max = baseline - 0.5 * (baseline - dip)
        
        # --- Find LEFT intersection (with interpolation) ---
        left_wl = None
        
        # Search left from peak
        for i in range(p, 0, -1):
            # Check if we cross the half-max line between points i and i-1
            if signal[i] >= half_max and signal[i-1] < half_max:
                # Linear interpolation
                x1, x2 = wavelengths[i-1], wavelengths[i]
                y1, y2 = signal[i-1], signal[i]
                left_wl = x1 + (x2 - x1) * (half_max - y1) / (y2 - y1)
                break
            elif signal[i] < half_max and signal[i-1] >= half_max:
                # Crossed in the other direction
                x1, x2 = wavelengths[i-1], wavelengths[i]
                y1, y2 = signal[i-1], signal[i]
                left_wl = x1 + (x2 - x1) * (half_max - y1) / (y2 - y1)
                break
        
        if left_wl is None:
            # If no crossing found, use the first point
            left_wl = wavelengths[0]
        
        # --- Find RIGHT intersection (with interpolation) ---
        right_wl = None
        
        # Search right from peak
        for i in range(p, len(signal)-1):
            # Check if we cross the half-max line between points i and i+1
            if signal[i] >= half_max and signal[i+1] < half_max:
                # Linear interpolation
                x1, x2 = wavelengths[i], wavelengths[i+1]
                y1, y2 = signal[i], signal[i+1]
                right_wl = x1 + (x2 - x1) * (half_max - y1) / (y2 - y1)
                break
            elif signal[i] < half_max and signal[i+1] >= half_max:
                # Crossed in the other direction
                x1, x2 = wavelengths[i], wavelengths[i+1]
                y1, y2 = signal[i], signal[i+1]
                right_wl = x1 + (x2 - x1) * (half_max - y1) / (y2 - y1)
                break
        
        if right_wl is None:
            # If no crossing found, use the last point
            right_wl = wavelengths[-1]
        
        # Calculate FWHM
        fwhm_val = abs(right_wl - left_wl)
        
        fwhms.append({
            "peak_index": p,
            "wl_left": left_wl,
            "wl_right": right_wl,
            "fwhm": fwhm_val
        })
        
        # Optional debug print
        # print(f"  Peak {wavelengths[p]:.2f} nm: FWHM={fwhm_val:.3f} nm")
    
    return fwhms

def calculate_q_factors(wavelengths, depths, fwhms):
    """Calculate Q and MQ factors for each peak."""
    q_factors = []
    for d, f in zip(depths, fwhms):
        peak_wl = float(wavelengths[d["peak_index"]])
        fwhm_val = float(f["fwhm"]) if f["fwhm"] > 0 else np.nan
        
        # Ensure positive values
        if fwhm_val and fwhm_val > 0:
            Q = peak_wl / fwhm_val
        else:
            Q = np.nan
        
        depth_val = abs(float(d["depth"]))  # Use absolute depth
        
        if not np.isnan(Q):
            MQ = Q * depth_val / 100  # Should be positive
        else:
            MQ = np.nan
        
        q_factors.append({
            "peak_index": d["peak_index"],
            "Q": Q,
            "MQ": MQ
        })
    
    return q_factors

def order_peaks_by_wavelength(depths, polarization=None):
    """
    Assign order to peaks based on increasing wavelength.
    P polarization: m = 1, -1 (first peak is m=1, second is m=-1)
    S polarization: m = 1, 2, 3...
    """
    # Sort by wavelength (increasing peak_index)
    sorted_depths = sorted(depths, key=lambda d: d["peak_index"])
    
    # Assign order based on polarization
    if polarization and polarization.upper() == 'P':
        # P polarization: m = 1, -1 (only for first two peaks)
        for i, d in enumerate(sorted_depths):
            if i == 0:
                d["order"] = 1      # First peak: m=1
            elif i == 1:
                d["order"] = -1     # Second peak: m=-1
            else:
                d["order"] = i + 1  # Additional peaks: m=2,3... (if any)
    else:
        # S polarization or unknown: m = 1, 2, 3...
        for i, d in enumerate(sorted_depths, start=1):
            d["order"] = i
    
    return sorted_depths

def analyze_signal(wavelengths, signal, column_name="", prominence=4, distance=10):
    """
    Compute peaks, depths, FWHM, Q, MQ, and assign resonance order.
    Returns a list of dictionaries ready for export.
    """
    # Detect polarization from column name
    polarization = None
    if " P " in column_name:
        polarization = "P"
    elif " S " in column_name:
        polarization = "S"
    
    peaks, props = detect_peaks(signal, prominence, distance)
    depths = calculate_depths(signal, peaks, props)
    depths = order_peaks_by_wavelength(depths, polarization)
    fwhms = calculate_fwhm(signal, wavelengths, peaks, props["left_bases"])
    q_factors = calculate_q_factors(wavelengths, depths, fwhms)
    
    results = []
    for d, f, q in zip(depths, fwhms, q_factors):
        results.append({
            "resonance_order": d["order"],  # m=-1, +1, +2... or m=1,2,3...
            # REMOVE THIS LINE: "peak_index": d["peak_index"],
            "peak_wl": float(wavelengths[d["peak_index"]]),
            "depth": abs(float(d["depth"])),
            "fwhm": float(f["fwhm"]),
            "Q": float(q["Q"]),
            "MQ": float(q["MQ"])
        })
    return results

def analyze_signal_with_custom_baseline(wavelengths, signal, column_name="", prominence=4, distance=10, custom_left_bases=None):
    """
    Same as analyze_signal but with manually adjusted baselines.
    custom_left_bases: list of baseline indices (one per peak)
    """
    # Detect polarization from column name
    polarization = None
    if " P " in column_name:
        polarization = "P"
    elif " S " in column_name:
        polarization = "S"
    
    peaks, props = detect_peaks(signal, prominence, distance)
    
    # Use custom baselines if provided
    if custom_left_bases is not None and len(custom_left_bases) == len(peaks):
        props["left_bases"] = np.array(custom_left_bases)
    
    depths = calculate_depths(signal, peaks, props)
    depths = order_peaks_by_wavelength(depths, polarization)
    fwhms = calculate_fwhm(signal, wavelengths, peaks, props["left_bases"])
    q_factors = calculate_q_factors(wavelengths, depths, fwhms)
    
    results = []
    for d, f, q in zip(depths, fwhms, q_factors):
        results.append({
            "resonance_order": d["order"],
            "peak_wl": float(wavelengths[d["peak_index"]]),
            "depth": abs(float(d["depth"])),
            "fwhm": float(f["fwhm"]),
            "Q": float(q["Q"]),
            "MQ": float(q["MQ"])
        })
    return results
