# MathWriting LaTeX Recognition — Final Project

This project trains a compact CNN+LSTM model to recognize handwritten math expressions and output LaTeX. It targets a modest GPU (GTX 1650 2GB) and includes a streaming dataset pipeline, scheduled sampling, preview decoding, beam search, and plotting of training curves.

## What A README Is
- A README explains what the project does, how to set it up, how to run it, and how to troubleshoot common issues. It’s the first document someone reads to understand and use your repo.

## Features
- Streaming `tf.data` pipeline for big datasets (100k–200k) without huge RAM spikes
- Compact CNN encoder + 2-layer LSTM decoder, BOS/EOS tokens
- Scheduled sampling (optional) to reduce exposure bias
- Beam search with penalties and heuristics for inference
- Preview decoding during training (epoch end)
- Matplotlib training curves saved as `training_curves.png`

## Requirements
- Windows 10/11, PowerShell 5.1
- Conda environment with TensorFlow GPU working on your NVIDIA driver
- Recommended: NVIDIA Studio/Game Ready driver (updated)

### Compatibility Notes (Windows + NVIDIA + TF)
- Windows supports NVIDIA GPU acceleration with TensorFlow 2.10 (last official TF GPU build for Windows).
- Verified environment here uses Python 3.10.13 and NumPy 2.2.6 in Conda.
- cuDNN 8.1 and CUDA v11.2 tooling are compatible with TF 2.10 on Windows.

Python packages (typical):
- tensorflow (GPU build), tensorflow-addons
- numpy, pillow, datasets (Hugging Face), scikit-learn
- matplotlib

## Project Structure
- `scripts/train.py` — training entrypoint (CLI flags for batch size, data limit, epochs)
- `scripts/predict.py` — inference entrypoint (loads `best_model.h5` or `model_gpu.h5`)
- `scripts/dataset.py` — dataset loader and streaming `tf.data` builders
- `scripts/model.py` — model architecture
- `scripts/inference_model.py` — step-wise encoder/decoder for inference
- `scripts/post_proc_script.py` — optional post-processing
- `scripts/tokenizer.py` — character tokenizer utilities
- `best_model.h5`, `model_gpu.h5`, `tokenizer.pkl` — saved artifacts
- `reference.bib` — bibliographic references for datasets/tools used

## Setup
1. Create and activate your conda env, install packages:
```powershell
conda activate tf2-gpu
pip install tensorflow-addons datasets pillow matplotlib scikit-learn
```
2. Verify GPU works:
```powershell
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```
Expected: a list containing `GPU:0`.

## Training
Run training with safe defaults for a 2GB GPU:
```powershell
conda activate tf2-gpu
cd "c:\Users\dovyd\OneDrive\Dokumentai\Univeras\CERN data analysis\final_project\scripts"
python .\train.py --batch-size 6 --data-limit 40000 --epochs 20
```
- `--batch-size`: small (6–8) to fit VRAM
- `--data-limit`: number of samples to load (streaming avoids RAM spikes)
- `--epochs`: training epochs
- Optional: `--scheduled-sampling --ss-prob 0.3`

Outputs:
- Saves `best_model.h5` (best val_loss) and `model_gpu.h5` (final state)
- Saves `tokenizer.pkl`
- Saves `training_curves.png` with loss/accuracy plots

## Prediction
Run inference on validation examples or your own image:
```powershell
conda activate tf2-gpu
cd "c:\Users\dovyd\OneDrive\Dokumentai\Univeras\CERN data analysis\final_project\scripts"
python .\predict.py --image ..\dataset\math_pngs\formula_098.png --beam 5 --output decoded.txt
```
- Uses `best_model.h5` by default; override with `--model model_gpu.h5`
- Prints predicted LaTeX; beam search with repeat/EOS penalties is enabled
- Optional flags:
	- `--image <path>`: input image path
	- `--beam <N>`: beam size (1=greedy)
	- `--model <path>`: explicit model file
	- `--length-norm <x>`: length normalization exponent
	- `--output <path>`: write decoded LaTeX to a file

### Batch Prediction & CSV
Predict multiple images at once and save a CSV for quick evaluation. You can provide a list, a glob pattern, or a numeric range.

Examples:
```powershell
# 1) Glob all JPGs in a folder
python .\predict.py --glob ..\dataset\hand_data\*.jpg --beam 5 --csv ..\output\predictions.csv

# 2) Explicit list
python .\predict.py --images ..\dataset\hand_data\1.jpg ..\dataset\hand_data\2.jpg ..\dataset\hand_data\7.jpg --beam 5 --csv ..\output\predictions.csv

# 3) Range 1..7 using name format "{:d}.jpg" in a directory
python .\predict.py --dir ..\dataset\hand_data --range-start 1 --range-end 7 --name-format "{:d}.jpg" --beam 5 --csv ..\output\predictions.csv
```
CSV columns: `filename`, `prediction`, `ground_truth` (left blank for you to fill).

Note: Batch prediction only reads models; it never overwrites `best_model.h5`, `model_gpu.h5`, or `model_final.h5`.

### Evaluate Predictions
After adding ground truths in the CSV, run:
```powershell
conda activate tf2-gpu
cd "c:\Users\dovyd\OneDrive\Dokumentai\Univeras\CERN data analysis\final_project\scripts"
python .\evaluate.py --csv ..\output\predictions.csv
```
Outputs exact-match accuracy and average Levenshtein distance, plus the top hardest examples.

## Tips for Large Datasets
- Streaming dataset is enabled to keep RAM stable even at 100k–200k.
- Keep `IMG_SIZE` modest (e.g., `(72,144)`); increase gradually if VRAM allows.
- Lower batch size first if you raise resolution.

## Demo
Quick demo assuming images named `1.jpg` to `7.jpg` exist under `dataset/hand_data`:
```powershell
conda activate tf2-gpu
cd "c:\Users\dovyd\OneDrive\Dokumentai\Univeras\CERN data analysis\final_project\scripts"
python .\predict.py --dir ..\dataset\hand_data --range-start 1 --range-end 7 --beam 5 --csv ..\output\demo_predictions.csv
```
Open the CSV in your editor and add the real LaTeX in the `ground_truth` column for quick evaluation.

## Troubleshooting
- Black screen / DWM reset: Windows GPU driver TDR. Use small batch size, moderate image size, update NVIDIA driver, close overlays. Relaunch training after the driver recovers.
- `nvidia-smi` fails: Install/update NVIDIA driver and reboot. Ensure the discrete GPU is active.
- `Dst tensor is not initialized`: We create large tensors on CPU or stream data to avoid GPU constant allocation issues.
- Slow validation: Validation runs over the full val set each epoch. Reduce val size, set `validation_steps`, or `validation_freq` in `train.py`.
- h5py/HDF5 mismatch warning: Generally safe; update h5py if needed.

## Common Commands
- Kill lingering Python processes before relaunching:
```powershell
Get-Process | Where-Object {$_.ProcessName -match "^python(\.exe)?$|^py(\.exe)?$"} | Stop-Process -Force
```
- Open training curves:
```powershell
Start-Process "c:\Users\dovyd\OneDrive\Dokumentai\Univeras\CERN data analysis\final_project\scripts\training_curves.png"
```

## Notes
- Cite sources: include `reference.bib` in your report to acknowledge dataset and libraries.
- This code is tuned for a small GPU; prefer minor architectural changes (attention, depthwise-separable convs) over large resolution jumps.
- Scheduled sampling can help reduce exposure bias; ramp or tune `--ss-prob` if needed.