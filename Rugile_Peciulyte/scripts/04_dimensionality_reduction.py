import os
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

DATA_PATH = "data/processed/train_engineered.csv"
FIGURES_DIR = "results/figures"

def main():
    df = pd.read_csv(DATA_PATH)

    # Separate numeric features and target
    y = df["critical_temp"]
    X = df.select_dtypes(include="number").drop(columns=["critical_temp"])

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA reduction to 2 components
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    pca_df = pd.DataFrame({
        "PC1": X_pca[:, 0],
        "PC2": X_pca[:, 1],
        "critical_temp": y
    })

    os.makedirs(FIGURES_DIR, exist_ok=True)

    fig = px.scatter(
        pca_df,
        x="PC1",
        y="PC2",
        color="critical_temp",
        color_continuous_scale="Viridis",
        title="PCA of Superconductivity Features",
        hover_data={"critical_temp": True}
    )

    # Save and show
    fig_path = os.path.join(FIGURES_DIR, "pca_2d.html")
    fig.write_html(fig_path)
    fig.show()
    print(f"[INFO] PCA figure saved to {fig_path}")

if __name__ == "__main__":
    main()
