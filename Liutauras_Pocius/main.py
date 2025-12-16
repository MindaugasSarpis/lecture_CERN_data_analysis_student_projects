from data_io import load_dimuon_csv
from physics import compute_invariant_mass, print_yields
from plots import (
    plot_mass,
    compare_masses,
    plot_z_fit,
    plot_pt_eta,
)


def main():
    df = load_dimuon_csv()
    # Recomputes the invariant mass and compares with the provided one
    m_csv = df["M"].to_numpy()
    m_reco = compute_invariant_mass(df)
    compare_masses(m_csv, m_reco)

    # The main mass spectrum is plotted in both linear and logaruthmic scales
    plot_mass(
        m_csv,
        m_range=(0.0, 125.0),
        logy=False,
        basename="dimuon_mass_linear",
    )
    plot_mass(
        m_csv,
        m_range=(0.0, 125.0),
        logy=True,
        basename="dimuon_mass_log",
    )

    # Computes and prints the yields
    print_yields(m_csv)

    # Fits and plots the data around the Z resonance peak
    plot_z_fit(m_csv)
    '''
    basic kinematic distributions
    '''
    plot_pt_eta(df)


if __name__ == "__main__":
    main()
