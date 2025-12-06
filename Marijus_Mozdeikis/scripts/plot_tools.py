import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from peak_tools import detect_peaks

# Interactive plotting with sliders and clickable baseline adjustment
def plot(wavelengths, signal, init_prom=4, init_dist=10, title="Signal"):

    final_values = {'prominence': init_prom, 'distance': init_dist, 'baselines': {}}
    
    # Initial detection
    peaks, props = detect_peaks(signal, init_prom, init_dist)
    final_values['baselines']['left_bases'] = props["left_bases"].copy()
    
    # Setup plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title(title)
    plt.subplots_adjust(bottom=0.25)
    
    # Plot
    ax.plot(wavelengths, signal, label="Signal")
    sc_peaks = ax.scatter(wavelengths[peaks], signal[peaks], s=30, color="red", label="Peaks", zorder=5)
    sc_left_base = ax.scatter(wavelengths[props["left_bases"]], signal[props["left_bases"]], 
                              s=20, color="green", marker='s', label="Baseline", zorder=5)
    
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Reflection (inverted)")
    ax.legend()
    
    # Sliders
    ax_prom = plt.axes([0.25, 0.10, 0.65, 0.03])
    ax_dist = plt.axes([0.25, 0.15, 0.65, 0.03])
    slider_prom = Slider(ax_prom, "Prominence", 0, 30, valinit=init_prom, valstep=0.5)
    slider_dist = Slider(ax_dist, "Distance", 0, 50, valinit=init_dist, valstep=2)
    
    # Click handling
    selected_peak = None
    
    def on_click(event):
        nonlocal selected_peak
        if event.inaxes != ax:
            return
        
        click_wl = event.xdata
        if peaks.size > 0:
            # Find closest peak
            idx = np.argmin(np.abs(wavelengths[peaks] - click_wl))
            selected_peak = peaks[idx]
    
    def on_click_baseline(event):
        nonlocal selected_peak
        if event.inaxes != ax or selected_peak is None:
            return
        
        # Find clicked point
        click_wl = event.xdata
        new_idx = np.argmin(np.abs(wavelengths - click_wl))
        
        # Update baseline
        if selected_peak in peaks:
            peak_idx = np.where(peaks == selected_peak)[0][0]
            final_values['baselines']['left_bases'][peak_idx] = new_idx
            
            # Update plot
            sc_left_base.set_offsets(np.c_[wavelengths[final_values['baselines']['left_bases']], 
                                          signal[final_values['baselines']['left_bases']]])
            
            selected_peak = None
            fig.canvas.draw()
    
    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('button_press_event', on_click_baseline)
    
    # Update function
    def update(_):
        prom = slider_prom.val
        dist = int(slider_dist.val)
        final_values['prominence'] = prom
        final_values['distance'] = dist
        
        peaks_new, props_new = detect_peaks(signal, prom, dist)
        if peaks_new.size > 0:
            peaks[:] = peaks_new
            props.update(props_new)
            final_values['baselines']['left_bases'] = props_new["left_bases"].copy()
            sc_peaks.set_offsets(np.c_[wavelengths[peaks], signal[peaks]])
            sc_left_base.set_offsets(np.c_[wavelengths[props_new["left_bases"]], signal[props_new["left_bases"]]])
        
        fig.canvas.draw_idle()
    
    slider_prom.on_changed(update)
    slider_dist.on_changed(update)
    update(None)
    
    plt.show()
    return final_values