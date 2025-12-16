import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load CSV files
white = pd.read_csv('C:/Users/gedim/OneDrive/Stalinis kompiuteris/Cern DAM/Gediminas Venclovas/dataset/winequality-white.csv', delimiter=';')
red = pd.read_csv('C:/Users/gedim/OneDrive/Stalinis kompiuteris/Cern DAM/Gediminas Venclovas/dataset/winequality-red.csv', delimiter=';')

# Columns we need
cols = ["alcohol", "pH", "free sulfur dioxide", "total sulfur dioxide"]

# Alcohol histogram
plt.figure(figsize=(8,5))
plt.hist(white["alcohol"], bins=40, alpha=0.6, label="White Wine", color="gold")
plt.hist(red["alcohol"], bins=40, alpha=0.6, label="Red Wine", color="darkred")
plt.xlabel("Alcohol")
plt.ylabel("Count")
plt.title("Alcohol Distribution")
plt.legend()
plt.savefig('C:/Users/gedim/OneDrive/Stalinis kompiuteris/Cern DAM/Gediminas Venclovas/output/alcohol_distribution.png')
plt.close()

# pH histogram
plt.figure(figsize=(8,5))
plt.hist(white["pH"], bins=40, alpha=0.6, label="White Wine", color="gold")
plt.hist(red["pH"], bins=40, alpha=0.6, label="Red Wine", color="darkred")
plt.xlabel("pH")
plt.ylabel("Count")
plt.title("pH Distribution")
plt.legend()
plt.savefig('C:/Users/gedim/OneDrive/Stalinis kompiuteris/Cern DAM/Gediminas Venclovas/output/pH_distribution.png')
plt.close()

# Total vs Free Sulfur Dioxide histograms (combined)
plt.figure(figsize=(8,5))
plt.hist(white["free sulfur dioxide"], bins=40, alpha=0.4, label="White Wine - Free SO₂", color="gold")
plt.hist(red["free sulfur dioxide"], bins=40, alpha=0.4, label="Red Wine - Free SO₂", color="darkred")
plt.hist(white["total sulfur dioxide"], bins=40, alpha=0.4, label="White Wine - Total SO₂", color="yellowgreen")
plt.hist(red["total sulfur dioxide"], bins=40, alpha=0.4, label="Red Wine - Total SO₂", color="firebrick")
plt.xlabel("SO₂ (mg/L)")
plt.ylabel("Count")
plt.title("Free & Total Sulfur Dioxide Distribution")
plt.legend()
plt.savefig('C:/Users/gedim/OneDrive/Stalinis kompiuteris/Cern DAM/Gediminas Venclovas/output/sulfur_dioxide_distribution.png')
plt.close()

# Correlation heatmaps
plt.figure(figsize=(6,5))
sns.heatmap(white[cols].corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap (White Wine)")
plt.savefig('C:/Users/gedim/OneDrive/Stalinis kompiuteris/Cern DAM/Gediminas Venclovas/output/correlation_heatmap_white.png')
plt.close()

plt.figure(figsize=(6,5))
sns.heatmap(red[cols].corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap (Red Wine)")
plt.savefig('C:/Users/gedim/OneDrive/Stalinis kompiuteris/Cern DAM/Gediminas Venclovas/output/correlation_heatmap_red.png')
plt.close()
