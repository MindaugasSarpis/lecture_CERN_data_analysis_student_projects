import numpy as np
from scipy.optimize import curve_fit

def gaussian(x, A, mu, sigma):
    return A * np.exp(-0.5 * ((x - mu) / sigma)**2)

def fit_z_peak(masses, m_min=80.0, m_max=100.0, nbins=120):
    mask = (masses >= m_min) & (masses <= m_max)
    m = masses[mask]

    counts, edges = np.histogram(m, bins=nbins, range=(m_min, m_max))
    centers = 0.5 * (edges[:-1] + edges[1:])
    '''
    initial guesses
    '''
    A0     = counts.max()
    mu0    = 91.0
    sigma0 = 2.0

    popt, pcov = curve_fit(gaussian, centers, counts, p0=[A0, mu0, sigma0])
    return centers, counts, popt, pcov
