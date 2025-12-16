# CMS Electron Classification Project

This project trains a neural network to classify CMS experiment events as **signal** or **background** using electron and jet features. The **signal** is defined as electron–positron pairs originating from the Drell–Yan process in proton–proton collisions. Any other events that contain a real electron pair—or events where detector imperfections cause other particles to be misidentified as electrons—are treated as **background noise**.

---

## Folder Structure
```
project_root/
│
├─ data/
│ ├─ raw/ # Raw ROOT files listed in txt
│ └─ processed/ # Preprocessed CSV dataset
│
├─ src/ # Python modules
│ ├─ __init__.py
│ ├─ preprocessing.py
│ └─ plot_training.py
│
├─ scripts/ # Scripts for dataset prep, training, evaluation
│ ├─ 1_prepare_dataset.py
│ ├─ 2_train.py
│ └─ 3_evaluate.py
│
├─ results/ # Trained models and plots
│ ├─ electron_classifier.h5
│ ├─ training_plot.png
│ ├─ auc_plot.png
│ └─ roc_plot.png
│
├─ environment.yml # Conda environment
└─ README.md 
```

## Requirements / Setup

**1. Clone the repository:**
``` bash
git clone https://github.com/Yokubas/lecture_CERN_data_analysis_student_projects

cd Jokubas_Maciulis
```
**2. Create the Conda environment:**
``` bash
conda env create -f environment.yml
conda activate cern_tf
```

## Usage

Run scripts from the project root using the ```-m``` flag to handle imports correctly:

**1. Prepare data set:**
``` bash
python -m scripts.1_prepare_dataset
```
- Loads signal and background ROOT files
- Flattens electrons and jets
- Saves proccesed dataset as ```data/processed/electron_dataset.csv```

**2. Train model**
``` bash
python -m scripts.2_train
```
- Trains a neural network on the preprocessed dataset
- Saves trained model as ```results/electron_classifier.h5```
- Generates plots for training history and AUC (```results/```)

**3. Evaluate model**
``` bash
python -m scripts.3_evaluate
```
- Loads saved model
- Computes predictions and ROC curve
- Saves evaluation plots (```results/roc_curve.png```)

## Notes
- Electron and jet features are flattened to a fixed number of objects per event.
- All features are standardized to mean 0 and standard deviation 1.
- Optional: class weights can be used in training to handle imbalanced datasets.

## References / Data
- Data used for training from the CMS experiment (NanoAODSIM format for 2016 collision data).
- Relevant Python libraries: ```pandas```, ```numpy```, ```awkward```, ```uproot```, ```tensorflow```, ```scikit-learn```, ```matplotlib```