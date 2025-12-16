from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from fit import gaussian, fit_z_peak


plt.style.use(["science", "notebook", "grid"]) # changes the style of plots


def plot_mass(
    masses: np.ndarray,
    outdir: str | Path = "figures",
    nbins: int = 300,
    m_range: tuple[float, float] = (0.0, 125.0),
    logy: bool = False,
    basename: str = "dimuon_mass",
) -> None:
    """
    Plots the dimuon invariant mass spectrum.
    Saves both PNG and PDF.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots()

    ax.hist(masses, bins=nbins, range=m_range, histtype="step")

    ax.set_xlabel(r"$m_{\mu\mu}$ [GeV]")
    ax.set_ylabel(r"Events / bin")
    ax.set_title(r"CMS Open Data: dimuon invariant mass")

    ax.set_xlim(*m_range)
    if logy:
        ax.set_yscale("log")

    fig.tight_layout()

    png_path = outdir / f"{basename}.png"
    pdf_path = outdir / f"{basename}.pdf"

    fig.savefig(png_path, dpi=300)
    fig.savefig(pdf_path)

    plt.close(fig)


def compare_masses(m_csv: np.ndarray, m_reco: np.ndarray,
                   outdir: str | Path = "figures") -> None:
    # Plots and print the difference M_csv - M_reco.
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    delta = m_csv - m_reco

    # Constructing the plot
    fig, ax = plt.subplots()
    ax.hist(delta, bins=100, histtype="step")
    ax.set_xlabel(r"$M_{\mathrm{CSV}} - M_{\mathrm{reco}}$ [GeV]")
    ax.set_ylabel(r"Events / bin")
    ax.set_title(r"Consistency of invariant mass reconstruction")
    fig.tight_layout()
    fig.savefig(outdir / "mass_difference.pdf")
    plt.close(fig)

    # Prints the mean mass difference
    print(f"ΔM mean = {delta.mean():.3e} GeV, RMS = {delta.std():.3e} GeV")


def plot_z_fit(masses: np.ndarray,
               outdir: str | Path = "figures") -> None:
    # Fits the Z peak with a Gaussian and plots data+fit.
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    centers, counts, (A, mu, sigma), pcov = fit_z_peak(masses) # Assigns the values of the fit function

    # Constructing the plot
    fig, ax = plt.subplots()
    ax.errorbar(centers, counts, yerr=np.sqrt(counts),
                fmt=".", label=r"Data")

    xfine = np.linspace(centers[0], centers[-1], 1000)
    ax.plot(xfine, gaussian(xfine, A, mu, sigma),
            label=r"Gaussian fit")

    ax.set_xlabel(r"$m_{\mu\mu}$ [GeV]")
    ax.set_ylabel(r"Events / bin")
    ax.set_title(r"$Z\rightarrow\mu^+\mu^-$ peak (Gaussian fit)")
    ax.legend(
    frameon=True,
    edgecolor='black',
    fancybox=False,
    framealpha=1.0,
    )
    fig.tight_layout()
    fig.savefig(outdir / "z_peak_fit.pdf")
    plt.close(fig)

    # Prints the mean and the width of the Gaussian fit
    print(f"Z fit: mu = {mu:.2f} GeV, sigma = {sigma:.2f} GeV")


def plot_pt_eta(df, outdir: str | Path = "figures") -> None:
    #Plots 1D distributions of pt1, pt2, eta1, eta2.
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    specs = [
        ("pt1",  r"$p_{T,1}$ [GeV]", "pt1"),
        ("pt2",  r"$p_{T,2}$ [GeV]", "pt2"),
        ("eta1", r"$\eta_1$",        "eta1"),
        ("eta2", r"$\eta_2$",        "eta2"),
    ]

    for col, xlabel, name in specs:
        fig, ax = plt.subplots()
        ax.hist(df[col], bins=100, histtype="step")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(r"Events / bin")
        ax.set_title(rf"Distribution of {col}")
        fig.tight_layout()
        fig.savefig(outdir / f"{name}.pdf")
        plt.close(fig)
