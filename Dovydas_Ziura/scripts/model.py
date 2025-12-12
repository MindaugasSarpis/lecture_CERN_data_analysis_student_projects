# model_fixed.py
from tensorflow.keras import layers, models, Input
from tensorflow.keras.optimizers import Adam
import tensorflow as tf
from config import MAX_SEQ_LEN


def build_model(vocab_size, output_seq_len=MAX_SEQ_LEN, learning_rate=0.001):
    # Accept variable-resolution inputs; pooling + GAP makes it size-agnostic
    img_input = Input(shape=(None, None, 1), name="encoder_input")
    x = layers.Conv2D(40, 3, padding='same', activation='relu')(img_input)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Conv2D(80, 3, padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Conv2D(128, 3, padding='same', activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D(2)(x)
    x = layers.Dropout(0.1)(x)
    # Replace huge Flatten with GlobalAveragePooling to reduce params/memory
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(256, activation='relu', name="encoder_fc")(x)

    init_h = layers.Dense(96, activation='relu', name="init_h")(x)
    init_c = layers.Dense(96, activation='relu', name="init_c")(x)

    dec_input = Input(shape=(None,), dtype='int32', name="decoder_input")
    emb = layers.Embedding(vocab_size, 64, mask_zero=True, name="decoder_embedding")(dec_input)
    emb = layers.Dropout(0.1)(emb)
    emb = layers.LayerNormalization(name="decoder_ln")(emb)

    lstm1 = layers.LSTM(96, return_sequences=True, return_state=True, name="decoder_lstm1")
    lstm2 = layers.LSTM(96, return_sequences=True, return_state=True, name="decoder_lstm2")

    lstm_out1 = lstm1(emb, initial_state=[init_h, init_c])
    lstm_out2 = lstm2(lstm_out1[0])  # only sequence output goes in

    proj = layers.Dense(96, activation='relu', name="proj")(lstm_out2[0])
    logits = layers.Dense(vocab_size, activation=None, name="decoder_logits")(proj)

    model = models.Model([img_input, dec_input], logits, name="MathWriter_v2")
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy']
    )
    return model
