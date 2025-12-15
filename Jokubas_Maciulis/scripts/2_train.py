import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from src.plot_training import plot_training_history, plot_auc

# Load CSV dataset
df = pd.read_csv("data/processed/electron_dataset.csv")

# Uncomment to check how balanced is your prepared dataset
# print(df['target'].value_counts())

# Separate features and target
X = df.drop(columns = ["target"]).to_numpy()
y = df["target"].to_numpy()

# Scale features to mean 0 and std 1 for stable and efficient training (does not get biased towards larger numerical values)
X = StandardScaler().fit_transform(X)

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Build feed-forward neural network
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X.shape[1],)), # Number of features per event
    tf.keras.layers.Dense(64),                  # First hidden layer with 64 neurons (fully connected)
    tf.keras.layers.LeakyReLU(),                # Activation function: introduces non-linearity; allows small gradient for negative inputs to keep learning

    tf.keras.layers.Dense(32),                  # Second hidden layer with 32 neurons
    tf.keras.layers.LeakyReLU(),                # Same as above, helps network learn complex patterns

    tf.keras.layers.Dense(16),                  # Third hidden layer with 16 neurons
    tf.keras.layers.LeakyReLU(),                # Same purpose: non-linearity + stable learning for negative inputs
    tf.keras.layers.Dense(1, activation="sigmoid")  # Output layer: 1 neuron, sigmoid activation
])                                                  # Outputs a probability between 0 and 1
                                                    # 1 → signal, 0 → background

model.summary() # Prints a summary of the network: layers, output shapes, and number of parameters

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),    # Adam optimizer adjusts weights efficiently; learning_rate controls step size
    loss="binary_crossentropy", # Loss function for binary classification: measures how far predictions are from true labels
    metrics=["accuracy",    # Fraction of correctly classified events (threshold 0.5)
             tf.keras.metrics.AUC(name="auc")] # ROC-AUC: evaluates signal vs background separation across all thresholds 
)

##############################################################
# Handling class imbalance (optional for balanced datasets) #
##############################################################
#
# If the number of signal events and background events is very different,
# the model might become biased toward the majority class. 
#
# To address this, you can compute class weights which give more 
# importance to the minority class during training:
#
# from sklearn.utils import class_weight
# class_weights = class_weight.compute_class_weight(
#     class_weight='balanced',
#     classes=np.unique(y_train),
#     y=y_train
# )
# class_weights_dict = dict(enumerate(class_weights))
#
# Then, pass these weights to model.fit:
#
# model.fit(
#     X_train, 
#     y_train, 
#     epochs=30, 
#     batch_size=128, 
#     validation_split=0.2, 
#     class_weight=class_weights_dict
# )

history = model.fit(
    X_train,                # Training features
    y_train,                # Training labels (signal=1, background=0)
    epochs=30,              # Number of times the model sees the full training data
    batch_size=128,         # Number of events processed before updating weights
    validation_split=0.2,   # 20% of training data used to monitor performance (not trained on)
    verbose=2               # Controls logging: 2 = progress per epoch
)

model.save("results/electron_classifier.h5")

plot_training_history(history, save_path="results/training_plot.png")

plot_auc(history, save_path="results/auc_plot.png")