# scripts/03_feature_importance.py

import os
import pandas as pd
import plotly.express as px

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

DATA_PATH = "data/processed/train_engineered.csv"
IMPORTANCE_PATH = "data/processed/"
FIGURES_DIR = "results/figures/"

def main():
    df = pd.read_csv(DATA_PATH)

    # Separate numeric features and target
    y = df["critical_temp"]
    X = df.select_dtypes(include="number").drop(columns=["critical_temp"])

    # baseline Random Forest
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Extract feature importance
    importance = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_
    }).sort_values(by="importance", ascending=False).head(20)

    importance.to_csv(IMPORTANCE_PATH + "feature_importances.csv", index=False)
    
    print("[INFO] Feature importances saved to data/processed/feature_importances.csv")

    os.makedirs(FIGURES_DIR, exist_ok=True)

    # Plot top 20 features
    fig = px.bar(
        importance,
        x="importance",
        y="feature",
        orientation="h",
        title="Top 20 Feature Importances (Random Forest)"
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))  # highest on top

    # Save figure
    fig_path = os.path.join(FIGURES_DIR, "feature_importance.html")
    fig.write_html(fig_path)
    fig.show()

    print(f"[INFO] Feature importance figure saved to {fig_path}")

if __name__ == "__main__":
    main()

