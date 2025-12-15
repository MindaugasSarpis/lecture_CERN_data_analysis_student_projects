from analysis_utils import (
    load_dataset,
    build_electrons,
    build_muons,
    build_jets,
    build_met,
    select_two_opposite_sign_same_flavour,
    z_mass_numpy,
    plot_hist,
    select_one_lepton,
    transverse_mass,
)


# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------
events = load_dataset()

# ------------------------------------------------------------
# Build physics objects
# ------------------------------------------------------------
electrons = build_electrons(events)
muons = build_muons(events)
jets = build_jets(events)
met_px, met_py, met_et = build_met(events)


# ------------------------------------------------------------
# Z -> ll Analysis
# ------------------------------------------------------------

two_el = select_two_opposite_sign_same_flavour(electrons)
two_mu = select_two_opposite_sign_same_flavour(muons)
Z_ee_mass = z_mass_numpy(two_el)
Z_mm_mass = z_mass_numpy(two_mu)
plot_hist(
    Z_ee_mass,
    bins=300,
    xlabel="m(ee) [GeV]",
    title="Z → ee Invariant Mass"
)

plot_hist(
    Z_mm_mass,
    bins=300,
    xlabel="m($\mu\mu$) [GeV]",
    title="Z → $\mu\mu$ Invariant Mass"
)

# ------------------------------------------------------------
# W -> lν Analysis
# ------------------------------------------------------------
one_lep_mask = select_one_lepton(electrons)
el = electrons[one_lep_mask][:, 0]

MT = transverse_mass(el, met_px[one_lep_mask], met_py[one_lep_mask])

plot_hist(
    MT,
    bins=300,
    xlabel="MT [GeV]",
    title="W Transverse Mass"
)


# ------------------------------------------------------------
# Jet Analysis (example: leading jet pT)
# ------------------------------------------------------------
leading_jets = jets[:, 0]
plot_hist(
    leading_jets.pt,
    bins=300,
    xlabel="Leading jet pT [GeV]",
    title="Leading Jet pT"
)
