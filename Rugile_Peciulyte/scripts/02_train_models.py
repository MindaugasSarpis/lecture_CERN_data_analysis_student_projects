import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

DATA_PATH = "data/processed/train_engineered.csv"
PREDICTION_PATH = "data/processed/"

def main():
    df = pd.read_csv(DATA_PATH)

    # Separate features and target
    y = df["critical_temp"]
    X = df.select_dtypes(include="number").drop(columns=["critical_temp"])


    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Train baseline model
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Predict on test set
    y_pred = model.predict(X_test)

    pred_df = pd.DataFrame({
        "true_critical_temp": y_test,
        "predicted_critical_temp": y_pred
    })
    pred_df.to_csv(PREDICTION_PATH + "critical_temp_predictions.csv", index=False)

    print(f"[INFO] Predictions saved to {PREDICTION_PATH}")

    # Evaluate
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)

    print("Baseline Random Forest results")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²: {r2:.3f}")
    # print("Shape of dataset:", df.shape)
    # print(df.columns.tolist())
    # print("Target in X:", "critical_temp" in X.columns)




if __name__ == "__main__":
    main()
