# Resonance Analysis Tool

Python tool for analyzing optical resonance spectra. Processes reflection measurements to extract resonance properties with interactive parameter adjustment.

## What It Does
- Loads reflection spectra from Excel files
- Inverts signals to detect resonance dips as peaks  
- Interactive plots with sliders for peak detection tuning
- Clickable baseline adjustment for accurate depth measurement
- Calculates: resonance wavelength, depth, FWHM, Q factor, MQ factor
- Exports results to Excel with controlled positioning
- Handles P and S polarization with correct resonance ordering

## Required Packages

- pandas numpy scipy matplotlib openpyxl
- python 3.14.0