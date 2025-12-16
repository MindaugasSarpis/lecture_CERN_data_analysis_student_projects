import os
import pandas as pd
import plotly.express as px

PROCESSED_CSV = "data/processed/train_engineered.csv"
FIGURES_DIR = "results/figures"

def main():
    if not os.path.exists(PROCESSED_CSV):
        raise FileNotFoundError(f"Processed CSV not found at {PROCESSED_CSV}. Run 00_prepare_data.py first.")
    df = pd.read_csv(PROCESSED_CSV)
    print(f"[INFO] Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    os.makedirs(FIGURES_DIR, exist_ok=True)

    # Quick overview of target variable (critical_temp)
    fig = px.histogram(df, x="critical_temp", nbins=50,
                       title="Distribution of Critical Temperature",
                       labels={"critical_temp": "Tc (K)"})
    fig.write_html(os.path.join(FIGURES_DIR, "distribution_tc.html"))
    fig.show()

    # Pairwise scatter plots for a few top features
    top_features = df.columns[1:6]
    for feature in top_features:
        fig = px.scatter(df, x=feature, y="critical_temp",
                         title=f"{feature} vs Critical Temperature",
                         labels={feature: feature, "critical_temp": "Tc (K)"},
                         opacity=0.6)
        fig.write_html(os.path.join(FIGURES_DIR, f"{feature}_vs_tc.html"))
        fig.show()

    # Correlation heatmap
    corr = df.select_dtypes("number").corr()
    fig = px.imshow(corr,
                    labels=dict(x="Feature", y="Feature", color="Correlation"),
                    title="Feature Correlation Heatmap")
    fig.write_html(os.path.join(FIGURES_DIR, "correlation_heatmap.html"))
    fig.show()

if __name__ == "__main__":
    main()
