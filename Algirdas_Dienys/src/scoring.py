import numpy as np

def score_metric(value, low, high):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0.0
    if low <= value <= high:
        return 100.0

    diff = (low - value) if value < low else (value - high)
    width = (high - low) if (high - low) != 0 else 1.0
    penalty = (diff / width) * 100.0
    return max(0.0, 100.0 - penalty)

def compute_daily_scores(df, targets):
    """
    targets: dict[str, (low, high)] for columns that exist in df
    Adds:
      <Metric> Score columns
      Daily Nutrition Score
    """
    out = df.copy()
    score_cols = []

    for metric, (low, high) in targets.items():
        if metric not in out.columns:
            raise ValueError(f"Target metric '{metric}' not found in df columns: {list(out.columns)}")
        sname = f"{metric} Score"
        out[sname] = out[metric].apply(lambda v: score_metric(v, low, high))
        score_cols.append(sname)

    out["Daily Nutrition Score"] = out[score_cols].mean(axis=1).round(1)
    return out