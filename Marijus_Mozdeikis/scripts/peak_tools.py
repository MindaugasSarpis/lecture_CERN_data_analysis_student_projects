from scipy.signal import find_peaks
import numpy as np

# Peak detection and analysis functions
def detect_peaks(signal, prominence, distance):
    return find_peaks(signal, prominence=prominence, distance=distance)

# Calculate depths of the detected peaks
def calculate_depths(signal, peaks, props):
    depths = []
    for p, lb in zip(peaks, props["left_bases"]):
        baseline, peak_val = signal[lb], signal[p]
        depths.append({
            "peak_index": p,
            "baseline_index": lb,
            "depth": baseline - peak_val
        })
    return depths

# Calculate FWHM using linear interpolation
def calculate_fwhm(signal, wavelengths, peaks, left_bases):
    fwhms = []
    for p, lb in zip(peaks, left_bases):
        baseline, dip = signal[lb], signal[p]
        half_max = baseline - 0.5 * (baseline - dip)
        
        # Find left crossing
        left_wl = wavelengths[0]
        for i in range(p, 0, -1):
            if (signal[i] >= half_max and signal[i-1] < half_max) or \
               (signal[i] < half_max and signal[i-1] >= half_max):
                x1, x2 = wavelengths[i-1], wavelengths[i]
                y1, y2 = signal[i-1], signal[i]
                left_wl = x1 + (x2 - x1) * (half_max - y1) / (y2 - y1)
                break
        
        # Find right crossing  
        right_wl = wavelengths[-1]
        for i in range(p, len(signal)-1):
            if (signal[i] >= half_max and signal[i+1] < half_max) or \
               (signal[i] < half_max and signal[i+1] >= half_max):
                x1, x2 = wavelengths[i], wavelengths[i+1]
                y1, y2 = signal[i], signal[i+1]
                right_wl = x1 + (x2 - x1) * (half_max - y1) / (y2 - y1)
                break
        
        fwhms.append({
            "peak_index": p,
            "fwhm": abs(right_wl - left_wl)
        })
    
    return fwhms

# Calculate Q and MQ factors
def calculate_q_factors(wavelengths, depths, fwhms):
    q_factors = []
    for d, f in zip(depths, fwhms):
        peak_wl = wavelengths[d["peak_index"]]
        fwhm_val = f["fwhm"]
        
        if fwhm_val > 0:
            Q = peak_wl / fwhm_val
            MQ = Q * abs(d["depth"]) / 100
        else:
            Q = MQ = np.nan
        
        q_factors.append({"Q": Q, "MQ": MQ})
    return q_factors

# Order peaks based on wavelength and polarization
def order_peaks_by_wavelength(depths, polarization=None):
    sorted_depths = sorted(depths, key=lambda d: d["peak_index"])
    
    if polarization and polarization.upper() == 'P':
        for i, d in enumerate(sorted_depths):
            d["order"] = 1 if i == 0 else (-1 if i == 1 else i + 1)
    else:
        for i, d in enumerate(sorted_depths, start=1):
            d["order"] = i
    
    return sorted_depths

# Main analysis function with custom baseline support
def analyze_signal(wavelengths, signal, column_name="", prominence=4, distance=10, custom_left_bases=None):
    
    polarization = "P" if " P " in column_name else "S" if " S " in column_name else None
    
    peaks, props = detect_peaks(signal, prominence, distance)
    
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