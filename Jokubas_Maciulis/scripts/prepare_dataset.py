import pandas as pd
from preprocessing import load_dataset_from_txt

signal_files = [
    "data/raw/signal/CMS_mc_RunIISummer20UL16NanoAODv9_DYJetsToLL_M-10to50_TuneCP5_13TeV-amcatnloFXFX-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_2520000_file_index.txt",
    "data/raw/signal/CMS_mc_RunIISummer20UL16NanoAODv9_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_30000_file_index.txt"
]

background_files = [
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_ST_t-channel_antitop_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_120000_file_index.txt",
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_ST_t-channel_top_5f_InclusiveDecays_TuneCP5_13TeV-powheg-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_120000_file_index.txt",
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_ST_tW_antitop_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_270000_file_index.txt",
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_ST_tW_top_5f_NoFullyHadronicDecays_TuneCP5_13TeV-powheg-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_2520000_file_index.txt",
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_2530000_file_index.txt",
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_WW_TuneCP5_13TeV-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_130000_file_index.txt",
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_WZ_TuneCP5_13TeV-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_110000_file_index.txt",
    "data/raw/background/CMS_mc_RunIISummer20UL16NanoAODv9_ZZ_TuneCP5_13TeV-pythia8_NANOAODSIM_106X_mcRun2_asymptotic_v17-v1_130000_file_index.txt"
]

branches = ["Electron_pt", "Electron_eta", "Electron_miniPFRelIso_all",
    "Electron_miniPFRelIso_chg", "Electron_dz", "Electron_dxy", "Electron_ip3d"]

# branches += [
#     "Jet_pt",
#     "Jet_eta",
#     "Jet_phi",
#     "Jet_btagDeepFlavB",
#     "Jet_nCharged"
# ]

dfs = []

signal_max = 200000
background_max = 100000

for f in signal_files:
    dfs.append(load_dataset_from_txt(f, target_label=1, max_events = signal_max, branches=branches))

for f in background_files:
    dfs.append(load_dataset_from_txt(f, target_label=0, max_events = background_max, branches=branches))

df = pd.concat(dfs, ignore_index=True)

# Shuffle dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv("data/processed/electron_dataset.csv", index=False)
