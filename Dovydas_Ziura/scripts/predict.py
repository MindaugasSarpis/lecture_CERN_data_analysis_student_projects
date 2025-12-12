# predict.py with optional beam search
from tensorflow.keras.models import load_model
import numpy as np
import pickle
import argparse
from tokenizer import sequence_to_text, BOS_TOKEN, EOS_TOKEN
from inference_model import build_inference_models
from dataset import preprocess_image, IMG_SIZE  # unified preprocessing
import re
from config import (
    MAX_SEQ_LEN,
    PREDICT_IMAGE,
    PREDICT_BEAM,
    PREDICT_LENGTH_NORM,
    PREDICT_MODEL,
    PREDICT_OUTPUT,
    PREDICT_TEMPERATURE,
    PREDICT_TOPK,
    PREDICT_TOPP,
    PREDICT_MIN_LEN,
    PREDICT_REPEAT_PENALTY,
    PREDICT_NGRAM_REPEAT,
)

# -----------------------------
# Step-by-step greedy decoding function
# -----------------------------
def softmax(x, temperature=1.0):
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-6, float(temperature))
    x = x - np.max(x)
    ex = np.exp(x)
    return ex / np.sum(ex)

def greedy_decode(encoder_states, decoder_model, start_id, end_id, max_len=150):
    h1, c1, h2, c2 = encoder_states
    decoded_ids = [start_id]
    for _ in range(max_len):
        token_input = np.array([[decoded_ids[-1]]])
        logits, h1, c1, h2, c2 = decoder_model.predict([token_input, h1, c1, h2, c2], verbose=0)
        logits_step = logits[0, 0] if logits.ndim == 3 else logits[0]
        next_id = int(np.argmax(logits_step))
        decoded_ids.append(next_id)
        if next_id == end_id:
            break
    return decoded_ids

def beam_decode(
    encoder_states,
    decoder_model,
    start_id,
    end_id,
    max_len=150,
    beam_size=5,
    length_norm=0.7,
    eos_bonus=0.2,
    repeat_penalty=0.15,
    ngram_repeat=3,
    temperature=1.0,
    topk=None,
    topp=None,
    min_len=5,
):
    h1, c1, h2, c2 = encoder_states
    beams = [{
        'seq': [start_id],
        'logp': 0.0,
        'states': (h1, c1, h2, c2),
        'finished': False
    }]
    finished = []
    for _ in range(max_len):
        new_beams = []
        for b in beams:
            if b['finished']:
                new_beams.append(b)
                continue
            last_id = b['seq'][-1]
            token_input = np.array([[last_id]])
            logits, nh1, nc1, nh2, nc2 = decoder_model.predict([token_input, b['states'][0], b['states'][1], b['states'][2], b['states'][3]], verbose=0)
            logits_step = logits[0, 0] if logits.ndim == 3 else logits[0]
            probs = softmax(logits_step, temperature=temperature)
            # optional nucleus/top-k filtering
            if topk is not None and topk > 0:
                top_idx = np.argpartition(probs, -topk)[-topk:]
                top_idx = top_idx[np.argsort(-probs[top_idx])]
            elif topp is not None and 0 < topp < 1.0:
                sorted_idx = np.argsort(-probs)
                cum = 0.0
                sel = []
                for idx in sorted_idx:
                    sel.append(idx)
                    cum += probs[idx]
                    if cum >= topp:
                        break
                top_idx = np.array(sel, dtype=np.int64)
            else:
                top_idx = np.argpartition(probs, -beam_size)[-beam_size:]
                top_idx = top_idx[np.argsort(-probs[top_idx])]
            for idx in top_idx:
                seq = b['seq'] + [int(idx)]
                # apply repeat penalty for immediate repeats and simple bi-gram loops
                rp = 0.0
                if len(seq) >= 2 and seq[-1] == seq[-2]:
                    rp += repeat_penalty
                if len(seq) >= 3 and seq[-1] == seq[-3]:
                    rp += repeat_penalty * 0.5
                nb = {
                    'seq': seq,
                    'logp': b['logp'] + float(np.log(probs[int(idx)] + 1e-12)) - rp,
                    'states': (nh1, nc1, nh2, nc2),
                    'finished': (int(idx) == end_id and len(seq) >= min_len)
                }
                new_beams.append(nb)
        def score(b):
            L = max(1, len(b['seq']) - 1)
            bonus = eos_bonus if b['finished'] else 0.0
            # simple brace balance penalty: count of '{' vs '}' tokens if available in tokenizer
            brace_pen = 0.0
            try:
                open_id = tokenizer.word_index.get('{')
                close_id = tokenizer.word_index.get('}')
                if open_id and close_id:
                    opens = sum(1 for t in b['seq'] if t == open_id)
                    closes = sum(1 for t in b['seq'] if t == close_id)
                    if opens > closes:
                        brace_pen += 0.05 * (opens - closes)
            except Exception:
                pass
            return (b['logp'] + bonus - brace_pen) / (L ** length_norm)
        new_beams.sort(key=score, reverse=True)
        beams = new_beams[:beam_size]
        if all(b['finished'] for b in beams):
            finished.extend(beams)
            break
    candidates = finished if finished else beams
    best = max(candidates, key=lambda b: (b['logp'] + (eos_bonus if b['finished'] else 0.0)) / (max(1, len(b['seq']) - 1) ** length_norm))
    return best['seq']

# -----------------------------
# Load trained model
# -----------------------------
def load_latest_model():
    print("[INFO] Loading model...")
    try:
        m = load_model("best_model.h5", compile=False)
        print("[INFO] Using model: best_model.h5")
        return m
    except Exception:
        m = load_model("model_gpu.h5", compile=False)
        print("[INFO] Using model: model_gpu.h5")
        return m

# -----------------------------
# Build inference encoder/decoder
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--image', type=str, default=PREDICT_IMAGE, help='Path to image file')
parser.add_argument('--images', nargs='*', help='List of image paths for batch prediction')
parser.add_argument('--glob', type=str, help='Glob pattern (e.g., ../dataset/hand_data/*.jpg) for batch prediction')
parser.add_argument('--dir', type=str, help='Directory for range-based batch prediction')
parser.add_argument('--range-start', type=int, help='Start index for range-based batch prediction (inclusive)')
parser.add_argument('--range-end', type=int, help='End index for range-based batch prediction (inclusive)')
parser.add_argument('--name-format', type=str, default='{:d}.jpg', help='Name format for range (e.g., "{:d}.jpg")')
parser.add_argument('--csv', type=str, help='Output CSV path for batch predictions')
parser.add_argument('--beam', type=int, default=PREDICT_BEAM, help='Beam size (1=greedy)')
parser.add_argument('--length-norm', type=float, default=PREDICT_LENGTH_NORM, help='Length normalization exponent')
parser.add_argument('--model', type=str, default=PREDICT_MODEL, help='Explicit model path to use (overrides best_model.h5/model_gpu.h5)')
parser.add_argument('--output', type=str, default=PREDICT_OUTPUT, help='Optional path to write decoded LaTeX')
parser.add_argument('--temperature', type=float, default=PREDICT_TEMPERATURE, help='Softmax temperature for sampling')
parser.add_argument('--topk', type=int, default=PREDICT_TOPK, help='Top-k filtering for beam expansion')
parser.add_argument('--topp', type=float, default=PREDICT_TOPP, help='Nucleus (top-p) filtering for beam expansion')
parser.add_argument('--min-len', type=int, default=PREDICT_MIN_LEN, help='Minimum generated length before allowing EOS')
parser.add_argument('--repeat-penalty', type=float, default=PREDICT_REPEAT_PENALTY, help='Penalty weight for repeats')
parser.add_argument('--ngram-repeat', type=int, default=PREDICT_NGRAM_REPEAT, help='n-gram size for repeat penalty (>=3)')
args = parser.parse_args()
if args.model:
    print(f"[INFO] Loading model override: {args.model}")
    training_model = load_model(args.model, compile=False)
    print(f"[INFO] Using model: {args.model}")
else:
    training_model = load_latest_model()
print("[INFO] Building inference models...")
encoder_model, decoder_model = build_inference_models(training_model)

print("[INFO] Loading tokenizer...")
with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)
print("[INFO] Tokenizer loaded. vocab_size=", getattr(tokenizer, "num_words", None) or len(getattr(tokenizer, "word_index", {})))

# Safe retrieval of BOS/EOS ids
start_id = tokenizer.word_index.get(BOS_TOKEN, 1)
end_id = tokenizer.word_index.get(EOS_TOKEN, 2)

def decode_one(img_path):
    print(f"[INFO] Preprocessing image: {img_path}")
    arr = preprocess_image(img_path)
    arr = np.expand_dims(arr, axis=0)
    print(f"[DEBUG] IMG_SIZE (from dataset.py): {IMG_SIZE}")
    print(f"[DEBUG] preprocessed image shape: {arr.shape}, dtype: {arr.dtype}, min/max: {float(arr.min())}/{float(arr.max())}")

    # Encoder forward pass
    h1, c1 = encoder_model.predict(arr)
    h2, c2 = np.zeros_like(h1), np.zeros_like(c1)

    # Decode
    if args.beam > 1:
        ids = beam_decode(
            encoder_states=(h1, c1, h2, c2),
            decoder_model=decoder_model,
            start_id=start_id,
            end_id=end_id,
            max_len=MAX_SEQ_LEN,
            beam_size=args.beam,
            length_norm=args.length_norm,
            temperature=args.temperature,
            topk=args.topk,
            topp=args.topp,
            min_len=args.min_len,
            repeat_penalty=args.repeat_penalty,
            ngram_repeat=args.ngram_repeat,
        )
    else:
        ids = greedy_decode(
            encoder_states=(h1, c1, h2, c2),
            decoder_model=decoder_model,
            start_id=start_id,
            end_id=end_id,
            max_len=MAX_SEQ_LEN,
        )

    # Convert to LaTeX
    ids_no_bos = ids[1:]
    latex_text = sequence_to_text(tokenizer, ids_no_bos)
    latex_text_clean = re.sub(r'(.)\1{1,}', r'\1', latex_text)
    latex_text_clean = latex_text_clean.replace(BOS_TOKEN, "").replace(EOS_TOKEN, "")
    return latex_text_clean

import os
import glob as _glob
import csv

def build_batch_list():
    paths = []
    if args.images:
        paths.extend(args.images)
    if args.glob:
        paths.extend(_glob.glob(args.glob))
    if args.range_start is not None and args.range_end is not None:
        base = args.dir or '.'
        for i in range(args.range_start, args.range_end + 1):
            name = args.name_format.format(i)
            paths.append(os.path.join(base, name))
    # de-duplicate while preserving order
    seen = set()
    uniq = []
    for p in paths:
        if p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq

batch_paths = build_batch_list()

if batch_paths:
    print(f"[INFO] Running batch prediction on {len(batch_paths)} images")
    rows = []
    for p in batch_paths:
        try:
            pred = decode_one(p)
            print(f"Decoded LaTeX ({p}): {pred}")
            rows.append({"filename": p, "prediction": pred, "ground_truth": ""})
        except Exception as e:
            print(f"[WARN] Failed to decode {p}: {e}")
            rows.append({"filename": p, "prediction": "", "ground_truth": "", "error": str(e)})

    if args.csv:
        try:
            with open(args.csv, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ["filename", "prediction", "ground_truth"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for r in rows:
                    writer.writerow({k: r.get(k, "") for k in fieldnames})
            print(f"[INFO] Saved batch predictions to {args.csv}")
        except Exception as e:
            print(f"[WARN] Could not write CSV {args.csv}: {e}")
else:
    # Single-image mode
    latex_text_clean = decode_one(args.image)
    print("Decoded LaTeX:", latex_text_clean)
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(latex_text_clean + "\n")
            print(f"[INFO] Saved decoded LaTeX to {args.output}")
        except Exception as e:
            print(f"[WARN] Could not write output file {args.output}: {e}")
