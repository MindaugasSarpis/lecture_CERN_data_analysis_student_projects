import os
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score


DATA_PATH = "data/processed/train_engineered.csv"
PREDICTION_PATH = "data/processed/critical_temp_predictions.csv"
IMPORTANCE_PATH = "data/processed/feature_importances.csv"
FIG_DIR = "results/figures/"

os.makedirs(FIG_DIR, exist_ok=True)

def report_theme(fig, x_label=None, y_label=None):
    
    fig.update_traces(marker=dict(size=5, opacity=0.7), selector=dict(type="scatter"))

    fig.update_layout(
        font=dict(family="Times New Roman", size=14, color="black"),
        xaxis_title=x_label, yaxis_title=y_label,
        coloraxis_colorbar = dict(tickfont=dict(size=14, family="Times New Roman", color="black"), 
            tickcolor="black", tickwidth=1.5, outlinewidth=1.5, outlinecolor="black"),        
        plot_bgcolor="white", paper_bgcolor="white"
    )

    fig.update_xaxes( showline=True, linewidth=1.5, linecolor="black", 
        ticks="inside", tickwidth=1.5, tickcolor="black", 
            tickfont=dict(size=16, family="Times New Roman", color="black") )

    fig.update_yaxes( showline=True, linewidth=1.5, linecolor="black",
        ticks="inside", tickwidth=1.5, tickcolor="black", 
            tickfont=dict(size=16, family="Times New Roman", color="black") )
    return fig

def generate_pca_figure():
    df = pd.read_csv(DATA_PATH)

    X = df.drop(columns=["critical_temp"])
    y = df["critical_temp"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    pca = PCA(n_components=2)
    pcs = pca.fit_transform(X_scaled)

    explained = pca.explained_variance_ratio_ * 100

    pca_df = pd.DataFrame({
        "PC1": pcs[:, 0],
        "PC2": pcs[:, 1],
        "critical_temp": y
    })

    fig = px.scatter(
        pca_df,
        x="PC1",
        y="PC2",
        color="critical_temp",
        color_continuous_scale="Viridis",
        labels={"critical_temp": "Critical Temperature (K)"}, 
    )

    fig = report_theme(
        fig,
        x_label=f"PC1 ({explained[0]:.1f}% variance)",
        y_label=f"PC2 ({explained[1]:.1f}% variance)"
    )

    fig.update_layout(width=550, height=400)

    fig.write_image(
        os.path.join(FIG_DIR, "pca_pc1_pc2.png"),
        scale=2
    )

    print("[INFO] PCA figure saved to results/figures/")

def generate_prediction_vs_true_figure():
    df = pd.read_csv(PREDICTION_PATH)

    rmse = np.sqrt(mean_squared_error(df["true_critical_temp"], df["predicted_critical_temp"]))
    r2 = r2_score(df["true_critical_temp"],df["predicted_critical_temp"])

    max_val=max(df["true_critical_temp"].max(), df["predicted_critical_temp"].max())
    max_val=np.ceil(max_val)

    fig = px.scatter(
        df,
        x="true_critical_temp",
        y="predicted_critical_temp",
        opacity=0.7
    )
 
    fig.add_shape(
        type="line",
        x0=0, y0=0, x1=max_val, y1=max_val,
        line=dict(color="maroon", dash="dash", width=2),
        layer="above"
    )

    fig.add_annotation(
        x=0.4 * max_val, xref="x",
        y=0.9 * max_val, yref="y",
        showarrow=False,
        text=f"R² = {r2:.3f}, RMSE = {rmse:.2f} K",
        font=dict(family="Times New Roman", size=14, color="black"),
        align="center"
    )

    fig = report_theme(fig, 
        x_label="Measured Critical Temperature (K)",
        y_label="Predicted Critical Temperature (K)"
    )

    fig.update_layout(
        legend=dict(x=0.1, y=0.9, xanchor="left", yanchor="top",
                    font=dict(family="Times New Roman", size=14, color="black")),
        width=400, height=400
    )

    fig.update_xaxes(range=[0, max_val], dtick=20, autorange=False)
    fig.update_yaxes(range=[0, max_val], dtick=20, scaleanchor="x", scaleratio=1)

    fig.write_image(
        os.path.join(FIG_DIR, "predicted_vs_true_tc.png"),
        scale=1
    )

    print("[INFO] Predicted vs. true Tc figure saved.")

def generate_feature_importance_figure():
    df = pd.read_csv(IMPORTANCE_PATH)
    df = df.sort_values("importance", ascending=False).head(10)
    fig = px.bar (
        df,
        x = "importance",
        y = "feature",
        orientation="h"
    )
    
    fig = report_theme(fig, x_label="Feature Importance", y_label="")
    
    fig.update_layout(height=350, width=700, margin=dict(l=80, r=10, t=10, b=30))
    fig.update_yaxes(tickfont=dict(size=14), autorange="reversed")
    fig.update_xaxes(tickfont=dict(size=14), rangemode="tozero", 
                     showgrid=True, gridwidth=0.5, gridcolor="rgba(0,0,0,0.15)", zeroline=False)

    fig.write_image(os.path.join(FIG_DIR, "feature_importance.png"), scale=2)

    print("[INFO] Feature importance figure saved.")

def main():
    generate_pca_figure()
    generate_prediction_vs_true_figure()
    generate_feature_importance_figure()

if __name__ == "__main__":
    main()
