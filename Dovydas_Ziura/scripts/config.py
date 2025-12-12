MAX_SEQ_LEN = 120
# Default batch size; can be overridden via CLI in train.py
BATCH_SIZE = 6
BATCH_SIZE = 6
# Default to 40000 samples; can be overridden via CLI in train.py
DATA_LIMIT = 100000
DATA_LIMIT = 100000
SEED = 45

#Image size used across dataset preprocessing and prediction (height, width)
IMAGE_SIZE = (60, 120)

# Prediction defaults (can be overridden via CLI in predict.py)
PREDICT_IMAGE = "../dataset/hand_data/prediction_test_8.jpg"
PREDICT_BEAM = 5  # 1=greedy; try 5 for better results
PREDICT_LENGTH_NORM = 0.7
PREDICT_MODEL = "best_model.h5"  # None -> prefer best_model.h5
PREDICT_OUTPUT = None  # Optional path to save decoded LaTeX

# Advanced decoding defaults
PREDICT_TEMPERATURE = 0.9
PREDICT_TOPK = 10  # e.g., 10
PREDICT_TOPP = 0.9  # e.g., 0.9
PREDICT_MIN_LEN = 8
PREDICT_REPEAT_PENALTY = 0.1
PREDICT_NGRAM_REPEAT = 3