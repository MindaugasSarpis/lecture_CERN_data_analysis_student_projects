from model import build_model
from tokenizer import create_char_tokenizer, texts_to_sequences
from dataset import load_mathwriting, preprocess_image, create_tf_dataset
import tensorflow as tf
import pickle
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from tensorflow.keras.mixed_precision import set_global_policy
from config import MAX_SEQ_LEN, BATCH_SIZE, DATA_LIMIT, SEED
from inference_model import decode_sequence, build_inference_models
import argparse
import types
import os
import random
import numpy as np
import matplotlib.pyplot as plt


# -------------------------------
# Mixed precision / GPU check
# -------------------------------
set_global_policy("float32")  # TF 2.10 mixed precision safe with float32

# -------------------------------
# Deterministic seeds
# -------------------------------
# Seed from shared config
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)
gpus = tf.config.list_physical_devices('GPU')
print("Num GPUs Available: ", len(gpus))
if len(gpus) == 0:
    print("WARNING: No GPU detected. Training will run on CPU.")

# -------------------------------
# Load dataset (limit for speed)
# -------------------------------
# Allow CLI override for data limit (set after args parsing). Temporarily use config; will reassign below.
(train_images, train_latex), (val_images, val_latex) = load_mathwriting(limit=DATA_LIMIT)

# If no val split, create one
if len(val_images) == 0:
    from sklearn.model_selection import train_test_split
    train_images, val_images, train_latex, val_latex = train_test_split(
        train_images, train_latex, test_size=0.1, random_state=SEED
    )

# -------------------------------
# Tokenizer
# -------------------------------
tokenizer = create_char_tokenizer(train_latex)
train_sequences = texts_to_sequences(tokenizer, train_latex, max_len=MAX_SEQ_LEN)
val_sequences = texts_to_sequences(tokenizer, val_latex, max_len=MAX_SEQ_LEN)
vocab_size = len(tokenizer.word_index) + 1  # include padding index
from tokenizer import BOS_TOKEN, EOS_TOKEN
pad_id = 0
bos_id = tokenizer.word_index.get(BOS_TOKEN, None)
eos_id = tokenizer.word_index.get(EOS_TOKEN, None)
print(f"[INFO] Vocab size: {vocab_size}, PAD={pad_id}, BOS={bos_id}, EOS={eos_id}")

# -------------------------------
# Preprocess images ONCE (CPU)
# -------------------------------
processed_train_images = [preprocess_image(img) for img in train_images]
processed_val_images = [preprocess_image(img) for img in val_images]

# -------------------------------
# Create ultra-fast TF datasets
# -------------------------------
# Batch size from config; may be overridden by CLI after args parsing.
train_dataset = create_tf_dataset(processed_train_images, train_sequences, batch_size=BATCH_SIZE)
val_dataset   = create_tf_dataset(processed_val_images, val_sequences, batch_size=BATCH_SIZE)

# -------------------------------
# Debug: Inspect one batch (after CLI overrides applied)
# -------------------------------
def _inspect_one_batch(ds, tokenizer):
    print("[DEBUG] Inspecting one training batch...")
    for ((dbg_imgs, dbg_dec_in), dbg_dec_out) in ds.take(1):
        print("[DEBUG] imgs:", dbg_imgs.shape, dbg_imgs.dtype, "min/max:", tf.reduce_min(dbg_imgs).numpy(), tf.reduce_max(dbg_imgs).numpy())
        print("[DEBUG] dec_in:", dbg_dec_in.shape, dbg_dec_in.dtype)
        print("[DEBUG] dec_out:", dbg_dec_out.shape, dbg_dec_out.dtype)
        from tokenizer import BOS_TOKEN, EOS_TOKEN
        bos_id = tokenizer.word_index.get(BOS_TOKEN, -1)
        eos_id = tokenizer.word_index.get(EOS_TOKEN, -1)
        print("[DEBUG] BOS id:", bos_id, "EOS id:", eos_id)
        bos_at_t0 = tf.reduce_sum(tf.cast(tf.equal(dbg_dec_in[:,0], bos_id), tf.int32)).numpy()
        print("[DEBUG] BOS at t=0 in dec_in:", bos_at_t0, "/", int(dbg_dec_in.shape[0]))
        eos_present = tf.reduce_sum(tf.cast(tf.reduce_any(tf.equal(dbg_dec_out, eos_id), axis=1), tf.int32)).numpy()
        print("[DEBUG] EOS present in dec_out (any position):", eos_present)
        unique_in = tf.unique(tf.reshape(dbg_dec_in, [-1]))[0]
        unique_out = tf.unique(tf.reshape(dbg_dec_out, [-1]))[0]
        print("[DEBUG] unique dec_in sample:", unique_in[:20].numpy())
        print("[DEBUG] unique dec_out sample:", unique_out[:20].numpy())
        break

# -------------------------------
# Build model
# -------------------------------
model = build_model(vocab_size, output_seq_len=MAX_SEQ_LEN-1)  # shift for decoder
model.summary()

# -------------------------------
# Callbacks
# -------------------------------
checkpoint_cb = ModelCheckpoint("best_model.h5", monitor="val_loss", save_best_only=True, verbose=1)
reduce_lr = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-5, verbose=1)
early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True, verbose=1)

# -------------------------------
# Training will be configured below (optionally with scheduled sampling)
# -------------------------------
# -------------------------------
# Scheduled sampling: simple generator and preview callback
# -------------------------------
def make_scheduled_train_step(ss_prob: float):
    ss_prob = tf.constant(ss_prob, dtype=tf.float32)

    @tf.function
    def train_step(self, data):
        (imgs, dec_in), dec_out = data
        with tf.GradientTape() as tape:
            # Teacher-forced pass to get per-step predictions
            logits_tf = self([imgs, dec_in], training=True)
            pred_ids = tf.argmax(logits_tf, axis=-1, output_type=tf.int32)
            # Random mask for scheduled sampling (exclude t=0 to keep BOS)
            rand = tf.random.uniform(tf.shape(dec_in), 0.0, 1.0)
            mask = tf.less(rand, ss_prob)
            batch = tf.shape(dec_in)[0]
            false_col = tf.zeros((batch, 1), dtype=tf.bool)
            mask = tf.concat([false_col, mask[:, 1:]], axis=1)
            # Mix predicted ids into decoder inputs
            new_dec_in = tf.where(mask, pred_ids, dec_in)
            # Final pass for loss/gradients
            logits = self([imgs, new_dec_in], training=True)
            loss = self.compiled_loss(dec_out, logits, regularization_losses=self.losses)

        grads = tape.gradient(loss, self.trainable_variables)
        self.optimizer.apply_gradients(zip(grads, self.trainable_variables))
        self.compiled_metrics.update_state(dec_out, logits)
        metrics = {m.name: m.result() for m in self.metrics}
        metrics['loss'] = loss
        return metrics

    return train_step
class PreviewDecodeCallback(tf.keras.callbacks.Callback):
    def __init__(self, val_images_np, val_texts, tokenizer, max_len):
        super().__init__()
        self.val_images_np = val_images_np
        self.val_texts = val_texts
        self.tokenizer = tokenizer
        self.max_len = max_len

    def on_epoch_end(self, epoch, logs=None):
        try:
            from inference_model import build_inference_models, decode_sequence
            tm = self.model
            enc, dec = build_inference_models(tm)
            print(f"\n[PREVIEW] Epoch {epoch+1}: decoding 3 validation samples...")
            for i in range(min(3, len(self.val_images_np))):
                gt = self.val_texts[i]
                img = self.val_images_np[i]
                pred = decode_sequence(img, enc, dec, self.tokenizer, max_len=self.max_len-1)
                print(f"[VAL {i}] GT: {gt}")
                print(f"[VAL {i}] PR: {pred}")
        except Exception as e:
            print("[PREVIEW] Skipped due to error:", e)

parser = argparse.ArgumentParser()
parser.add_argument('--scheduled-sampling', action='store_true', help='Enable scheduled sampling')
parser.add_argument('--ss-prob', type=float, default=0.3, help='Scheduled sampling probability')
parser.add_argument('--batch-size', type=int, default=None, help='Override batch size (default from config)')
parser.add_argument('--data-limit', type=int, default=None, help='Override dataset size limit (default from config)')
parser.add_argument('--epochs', type=int, default=10, help='Number of training epochs')
args = parser.parse_args()

# If CLI overrides are provided, rebuild datasets accordingly
if args.data_limit is not None:
    (train_images, train_latex), (val_images, val_latex) = load_mathwriting(limit=args.data_limit)
    # Re-tokenize and preprocess if data changed
    # If no val split, create one
    if len(val_images) == 0:
        from sklearn.model_selection import train_test_split
        train_images, val_images, train_latex, val_latex = train_test_split(
            train_images, train_latex, test_size=0.1, random_state=SEED
        )

    tokenizer = create_char_tokenizer(train_latex)
    train_sequences = texts_to_sequences(tokenizer, train_latex, max_len=MAX_SEQ_LEN)
    val_sequences = texts_to_sequences(tokenizer, val_latex, max_len=MAX_SEQ_LEN)
    processed_train_images = [preprocess_image(img) for img in train_images]
    processed_val_images = [preprocess_image(img) for img in val_images]

if args.batch_size is not None:
    train_dataset = create_tf_dataset(processed_train_images, train_sequences, batch_size=args.batch_size)
    val_dataset   = create_tf_dataset(processed_val_images, val_sequences, batch_size=args.batch_size)

# Inspect after final dataset construction
_inspect_one_batch(train_dataset, tokenizer)

preview_cb = PreviewDecodeCallback(
    val_images_np=processed_val_images,
    val_texts=val_latex,
    tokenizer=tokenizer,
    max_len=MAX_SEQ_LEN,
)

if args.scheduled_sampling:
    print(f"[INFO] Using scheduled sampling with p={args.ss_prob}")
    # Monkey-patch train_step with a vectorized scheduled sampling implementation
    model.train_step = make_scheduled_train_step(args.ss_prob).__get__(model, tf.keras.Model)

history = model.fit(
    train_dataset,
    epochs=args.epochs,
    validation_data=val_dataset,
    callbacks=[checkpoint_cb, reduce_lr, early_stop, preview_cb],
    verbose=1
)

# Save model & tokenizer after training
model.save("model_gpu.h5")
with open("tokenizer.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

print("Training finished successfully!")

# -------------------------------
# Plot training curves
# -------------------------------
try:
    hist = history.history
    epochs_range = range(1, len(hist.get('loss', [])) + 1)

    plt.figure(figsize=(10, 4))
    # Loss plot
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, hist.get('loss', []), label='train')
    plt.plot(epochs_range, hist.get('val_loss', []), label='val')
    plt.title('Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()

    # Accuracy plot
    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, hist.get('accuracy', []), label='train')
    plt.plot(epochs_range, hist.get('val_accuracy', []), label='val')
    plt.title('Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()

    plt.tight_layout()
    plt.savefig('training_curves.png')
    print('Saved training curves to training_curves.png')
except Exception as e:
    print('[WARN] Could not plot training curves:', e)

# -------------------------------
# Training finished, now run inference
# -------------------------------
from inference_model import build_inference_models, decode_sequence

# Load trained model
training_model = model

# Build inference models
encoder_model, decoder_model = build_inference_models(training_model)

# Pick an image from validation set if available
if len(processed_val_images) > 0:
    img = processed_val_images[0]
    gt_latex = val_latex[0]

    # Also show the ground-truth label for this image
    print("[INFO] Ground-truth LaTeX for val[0]:", gt_latex)
    try:
        # Show its token ids for reference
        from tokenizer import texts_to_sequences
        gt_seq = texts_to_sequences(tokenizer, [gt_latex], max_len=MAX_SEQ_LEN)
        print("[INFO] Ground-truth token ids:", gt_seq[0].tolist())
    except Exception as e:
        print("[WARN] Could not display token ids:", e)

    # Decode
    decoded_text = decode_sequence(img, encoder_model, decoder_model, tokenizer, max_len=MAX_SEQ_LEN-1)
    print("Decoded LaTeX:", decoded_text)
else:
    print("[INFO] No validation samples available to preview decoding.")
