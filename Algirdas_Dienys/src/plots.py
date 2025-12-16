import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def scatter_with_line(df, x, y, outpath=None, title=None):
    """
    Create a scatter plot of y vs x with a linear best-fit line.
    Returns the slope, intercept, and Pearson correlation coefficient.
    """

    # drop NaNs 
    d = df[[x, y]].dropna()
    m, b = np.polyfit(d[x], d[y], 1)
    corr = d[[x, y]].corr().iloc[0, 1]

    plt.figure(figsize=(7,5))
    plt.scatter(d[x], d[y])
    xs = np.linspace(d[x].min(), d[x].max(), 100)
    plt.plot(xs, m*xs + b)

    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title or f"{y} vs {x}  |  slope={m:.4g}, r={corr:.3f}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if outpath:
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        plt.savefig(outpath, dpi=200)
    plt.show()

    return m, b, corr

def score_histogram(df, outpath=None):
    """
    Plot a histogram of daily nutrition scores using 10-point bins (0–100).
    Optionally saves the figure to the given output path.
    """
    scores = df["Daily Nutrition Score"].dropna()

    plt.figure(figsize=(7,5))
    bins = list(range(0, 110, 10))
    plt.hist(scores, bins=bins)

    plt.xticks(range(0, 110, 10))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))  # whole-number y ticks, no floats

    plt.xlabel("Daily Nutrition Score")
    plt.ylabel("Count of Days")
    plt.title("Distribution of Daily Nutrition Scores (10-point bins)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if outpath:
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        plt.savefig(outpath, dpi=200)
    plt.show()