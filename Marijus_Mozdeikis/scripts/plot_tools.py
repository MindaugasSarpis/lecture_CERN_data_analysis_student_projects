import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from peak_tools import detect_peaks, calculate_depths, calculate_fwhm

def plot_with_sliders_and_baseline(wavelengths, signal, init_prom=4, init_dist=10, title="Signal"):
    """Interactive plot with sliders AND clickable baseline adjustment."""
    
    final_values = {'prominence': init_prom, 'distance': init_dist, 'baselines': {}}
    
    # --- Initial detection ---
    peaks, props = detect_peaks(signal, init_prom, init_dist)
    final_values['baselines']['left_bases'] = props["left_bases"].copy()
    
    # --- Figure ---
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(title + "\nClick near baseline to adjust, then press Enter")
    plt.subplots_adjust(bottom=0.25)
    
    # --- Main plot ---
    ax.plot(wavelengths, signal, label="Signal")
    
    # Peak and baseline scatter plots
    sc_peaks = ax.scatter(wavelengths[peaks], signal[peaks], s=50, color="red", label="Peaks", zorder=5)
    sc_left_base = ax.scatter(wavelengths[props["left_bases"]], signal[props["left_bases"]], 
                              s=60, color="green", marker='s', label="Left Baseline", zorder=5)
    
    # Add vertical lines to show baseline positions
    vlines = []
    for lb_idx in props["left_bases"]:
        vline = ax.axvline(wavelengths[lb_idx], color='green', alpha=0.3, linestyle='--', zorder=3)
        vlines.append(vline)
    
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflection (inverted)")
    ax.legend()
    
    # --- Sliders ---
    ax_prom = plt.axes([0.25, 0.10, 0.65, 0.03])
    ax_dist = plt.axes([0.25, 0.15, 0.65, 0.03])
    slider_prom = Slider(ax_prom, "Prominence", 0, 30, valinit=init_prom, valstep=0.5)
    slider_dist = Slider(ax_dist, "Min Distance", 0, 50, valinit=init_dist, valstep=2)
    
    # --- Click handling ---
    selected_peak = None
    
    def on_click(event):
        nonlocal selected_peak
        if event.inaxes != ax:
            return
        
        # Find closest peak to click
        click_wl = event.xdata
        if peaks.size > 0:
            peak_distances = np.abs(wavelengths[peaks] - click_wl)
            closest_idx = np.argmin(peak_distances)
            selected_peak = peaks[closest_idx]
            
            # Highlight selected peak
            for artist in ax.collections:
                if artist.get_label() == "Selected Peak":
                    artist.remove()
            
            ax.scatter(wavelengths[selected_peak], signal[selected_peak], 
                      s=80, color='orange', marker='*', label="Selected Peak", zorder=6)
            fig.canvas.draw()
            print(f"\nSelected peak at λ={wavelengths[selected_peak]:.2f} nm")
            print("Now click where the baseline should be for this peak...")
    
    def on_click_baseline(event):
        nonlocal selected_peak
        if event.inaxes != ax or selected_peak is None:
            return
        
        # Find closest data point to click
        click_wl = event.xdata
        closest_idx = np.argmin(np.abs(wavelengths - click_wl))
        
        # Update baseline for this peak
        if selected_peak in peaks:
            peak_idx_in_array = np.where(peaks == selected_peak)[0][0]
            final_values['baselines']['left_bases'][peak_idx_in_array] = closest_idx
            
            # Update visualization
            sc_left_base.set_offsets(np.c_[wavelengths[final_values['baselines']['left_bases']], 
                                          signal[final_values['baselines']['left_bases']]])
            
            # Update vertical line
            if peak_idx_in_array < len(vlines):
                vlines[peak_idx_in_array].set_xdata([wavelengths[closest_idx], wavelengths[closest_idx]])
            
            print(f"  Baseline moved to λ={wavelengths[closest_idx]:.2f} nm")
            print(f"  New baseline value: {signal[closest_idx]:.3f}")
            
            # Calculate new depth
            new_depth = signal[closest_idx] - signal[selected_peak]
            print(f"  New depth: {abs(new_depth):.3f}")
            
            selected_peak = None
            fig.canvas.draw()
    
    # Connect click events
    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('button_press_event', on_click_baseline)
    
    # --- Update function ---
    def update(_):
        prom = slider_prom.val
        dist = int(slider_dist.val)
        final_values['prominence'] = prom
        final_values['distance'] = dist
        
        peaks_new, props_new = detect_peaks(signal, prom, dist)
        
        # Update peaks
        if peaks_new.size > 0:
            peaks[:] = peaks_new
            props.update(props_new)
            final_values['baselines']['left_bases'] = props_new["left_bases"].copy()
            
            sc_peaks.set_offsets(np.c_[wavelengths[peaks], signal[peaks]])
            sc_left_base.set_offsets(np.c_[wavelengths[props_new["left_bases"]], signal[props_new["left_bases"]]])
            
            # Update vertical lines
            for vline in vlines:
                vline.remove()
            vlines.clear()
            
            for lb_idx in props_new["left_bases"]:
                vline = ax.axvline(wavelengths[lb_idx], color='green', alpha=0.3, linestyle='--', zorder=3)
                vlines.append(vline)
            
            print(f"\n=== {title} ===")
            print(f"Prominence={prom}, Distance={dist}")
            print(f"Detected {len(peaks)} peaks")
    
        fig.canvas.draw_idle()
    
    slider_prom.on_changed(update)
    slider_dist.on_changed(update)
    update(None)
    
    print("\n" + "="*50)
    print("INSTRUCTIONS:")
    print("1. First click on a peak (red dot) to select it")
    print("2. Then click where the baseline should be")
    print("3. Adjust sliders as needed")
    print("4. Close window when done")
    print("="*50)
    
    plt.show()
    return final_values