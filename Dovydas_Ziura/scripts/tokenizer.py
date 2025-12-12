from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np

# Use single-character BOS/EOS tokens for char-level tokenization
BOS_TOKEN = "\x01"  # Start-of-text
EOS_TOKEN = "\x02"  # End-of-text

def create_char_tokenizer(latex_texts, num_chars=5000):
    """
    Character-level tokenizer with single-char BOS/EOS tokens.
    """
    # Add BOS/EOS to each formula
    enhanced_texts = [BOS_TOKEN + t + EOS_TOKEN for t in latex_texts]

    tok = Tokenizer(
        num_words=num_chars,
        filters="", 
        lower=False,
        char_level=True
    )
    tok.fit_on_texts(enhanced_texts)

    return tok


def texts_to_sequences(tok, texts, max_len=150):
    """
    Converts a list of strings to padded sequences with BOS/EOS added.
    """
    enhanced = [BOS_TOKEN + t + EOS_TOKEN for t in texts]
    sequences = tok.texts_to_sequences(enhanced)
    padded = pad_sequences(
        sequences,
        maxlen=max_len,
        padding='post',
        truncating='post'
    )
    return padded.astype(np.int32)


def sequence_to_text(tok, seq):
    """
    Converts a sequence of integers back into text.
    Strips BOS/EOS and padding.
    """
    index_word = tok.index_word
    chars = []

    for idx in seq:
        if idx == 0:  # padding
            continue
        ch = index_word.get(idx, "")
        if ch in (BOS_TOKEN, EOS_TOKEN):
            continue
        chars.append(ch)

    return "".join(chars)
