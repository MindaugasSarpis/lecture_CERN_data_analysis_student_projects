from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from model import build_model  # uses current model definition
import numpy as np

def build_inference_models(training_model):
    """
    Creates encoder and decoder models for step-by-step inference.
    Handles two stacked LSTM layers properly.
    """

    # -----------------------------
    # Encoder model
    # -----------------------------
    encoder_input = training_model.get_layer("encoder_input").input
    init_h = training_model.get_layer("init_h").output
    init_c = training_model.get_layer("init_c").output

    encoder_model = Model(inputs=encoder_input, outputs=[init_h, init_c], name="encoder_model")

    # -----------------------------
    # Decoder model
    # -----------------------------
    decoder_input = training_model.get_layer("decoder_input").input
    dec_emb_layer = training_model.get_layer("decoder_embedding")
    dec_ln_layer = training_model.get_layer("decoder_ln")
    lstm1_layer = training_model.get_layer("decoder_lstm1")
    lstm2_layer = training_model.get_layer("decoder_lstm2")
    proj_layer = training_model.get_layer("proj")
    logits_layer = training_model.get_layer("decoder_logits")

    # Dynamic state sizes from the training model
    u1 = lstm1_layer.units
    u2 = lstm2_layer.units

    # Step input tokens
    token_in = Input(shape=(1,), dtype='int32', name="token_in")
    # Previous LSTM states
    h1_in = Input(shape=(u1,), name="h1_in")
    c1_in = Input(shape=(u1,), name="c1_in")
    h2_in = Input(shape=(u2,), name="h2_in")
    c2_in = Input(shape=(u2,), name="c2_in")

    # Embedding + LayerNorm
    emb = dec_emb_layer(token_in)
    emb = dec_ln_layer(emb)

    # LSTM layers
    lstm1_out, h1_out, c1_out = lstm1_layer(emb, initial_state=[h1_in, c1_in])
    lstm2_out, h2_out, c2_out = lstm2_layer(lstm1_out, initial_state=[h2_in, c2_in])

    # Projection + logits
    proj = proj_layer(lstm2_out)
    logits = logits_layer(proj)

    decoder_model = Model(
        inputs=[token_in, h1_in, c1_in, h2_in, c2_in],
        outputs=[logits, h1_out, c1_out, h2_out, c2_out],
        name="decoder_model"
    )

    return encoder_model, decoder_model


BOS_TOKEN = "<s>"
EOS_TOKEN = "</s>"

from tokenizer import sequence_to_text

import numpy as np

def decode_sequence(image, encoder_model, decoder_model, tokenizer, max_len=150):
    """
    Decode a single preprocessed image into a LaTeX string.
    """
    # 1) Encode the image
    h1, c1 = encoder_model.predict(np.expand_dims(image, axis=0), verbose=0)
    # For the second LSTM layer, start with zeros
    h2, c2 = np.zeros_like(h1), np.zeros_like(c1)

    # 2) Initialize output sequence with BOS token
    token_idx = tokenizer.word_index["\x01"]  # BOS
    output_seq = [token_idx]

    for _ in range(max_len):
        token_array = np.array([[token_idx]], dtype=np.int32)
        logits, h1, c1, h2, c2 = decoder_model.predict([token_array, h1, c1, h2, c2], verbose=0)
        token_idx = np.argmax(logits[0, 0, :])

        # Stop at EOS
        if token_idx == tokenizer.word_index["\x02"]:
            break

        output_seq.append(token_idx)

    # --- FIX: use our custom sequence_to_text ---
    from tokenizer import sequence_to_text
    return sequence_to_text(tokenizer, output_seq)





# Example usage (optional)
if __name__ == "__main__":
    from tensorflow.keras.models import load_model
    training_model = load_model("model_gpu.h5")
    encoder_model, decoder_model = build_inference_models(training_model)

    # Dummy input sequence
    input_seq = np.array([[1, 5, 7, 9]])
    start_token_id = 0
    eos_token_id = 2

    decoded_tokens = decode_sequence(
        encoder_model, decoder_model, input_seq, start_token_id, eos_token_id
    )
    print("Decoded tokens:", decoded_tokens)
