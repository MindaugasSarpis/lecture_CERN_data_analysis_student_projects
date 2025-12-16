import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_curve, auc

df = pd.read_csv("data/processed/electron_dataset.csv")

X = df.drop(columns=["target"]).to_numpy()
y = df["target"].to_numpy()

X = StandardScaler().fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = tf.keras.models.load_model("results/electron_classifier.h5")

# Predicts probabilities and flattens 2D array to 1D
y_scores = model.predict(X_test).ravel()

# Compute the False Positive Rate (FPR) and True Positive Rate (TPR)
# for various probability thresholds. This is used to create the ROC curve.
fpr, tpr, thresholds = roc_curve(y_test, y_scores)

# Compute the Area Under the Curve (AUC) from the FPR and TPR.
# AUC summarizes the model's ability to distinguish signal from background:
# - 1.0  -> perfect separation
# - 0.5  -> random guessing
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, lw=2, label=f"ROC curve (AUC = {roc_auc:.3f})")
plt.plot([0, 1], [0, 1], linestyle="--", label="Random classifier")
plt.xlabel("False Positive Rate (Background Accepted)")
plt.ylabel("True Positive Rate (Signal Efficiency)")
plt.legend()
plt.grid()
plt.savefig("results/roc_curve.png", dpi=300)
plt.show()



