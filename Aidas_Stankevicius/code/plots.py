import matplotlib.pyplot as plt
import pandas as pd


def show_positions(driver_df: pd.DataFrame):
    display_df = driver_df[["round", "race_name", "position", "points"]].copy()
    display_df["position"] = display_df["position"].apply(lambda x: "DNF" if x == 99 else x)

    print("\nFinishing positions:")
    print(display_df[["round", "race_name", "position"]].to_string(index=False))

    do_plot = input("Show graph? (y/n): ").strip().lower()
    if do_plot != "y":
        return

    want_legend = input("Show legend? (y/n): ").strip().lower() == "y"
    legend_loc = None
    if want_legend:
        print("\nLegend position:")
        print("1 - Upper right")
        print("2 - Upper left")
        print("3 - Lower right")
        print("4 - Lower left")
        print("5 - Best")

        loc_map = {
            "1": "upper right",
            "2": "upper left",
            "3": "lower right",
            "4": "lower left",
            "5": "best",
        }

        while True:
            c = input("Choose legend position (1–5): ").strip()
            if c in loc_map:
                legend_loc = loc_map[c]
                break
            print("Invalid choice, try again.")

    wins = driver_df[driver_df["position"] == 1]
    podiums = driver_df[(driver_df["position"] >= 2) & (driver_df["position"] <= 3)]
    points_finish = driver_df[(driver_df["position"] > 3) & (driver_df["points"] > 0)]
    no_points_finish = driver_df[(driver_df["position"] > 3) & (driver_df["points"] == 0)]
    dnfs = driver_df[driver_df["position"] == 99]

    finished_positions = driver_df[driver_df["position"] < 99]["position"]
    worst_finish = int(finished_positions.max()) if not finished_positions.empty else 20

    top_padding = 0.8
    bottom_padding = 2.0
    y_min = 1 - top_padding
    y_max = worst_finish + bottom_padding

    plt.figure(figsize=(11, 5))

    plt.scatter(wins["round"], wins["position"], color="green", s=90, label="Win (P1)", zorder=3)
    plt.scatter(podiums["round"], podiums["position"], color="gold", s=90, label="Podium (P2–P3)", zorder=3)
    plt.scatter(points_finish["round"], points_finish["position"],
                color="royalblue", s=70, label="Points finish", zorder=3)
    plt.scatter(no_points_finish["round"], no_points_finish["position"],
                color="red", s=70, label="No points finish", zorder=3)

    if not dnfs.empty:
        dnf_y = worst_finish + bottom_padding * 0.8
        plt.scatter(
            dnfs["round"],
            [dnf_y] * len(dnfs),
            color="red",
            marker="x",
            s=90,
            label="DNF",
            zorder=4,
        )

    plt.ylim(y_max, y_min)
    plt.xlabel("Round")
    plt.ylabel("Finishing position")
    plt.title(f"{driver_df['driver_name'].iloc[0]} – Finishing positions")

    plt.yticks(range(1, worst_finish + 1))
    plt.xticks(driver_df["round"])
    plt.grid(True, which="both", axis="both", linestyle="--", alpha=0.5)

    if want_legend:
        plt.legend(loc=legend_loc)

    plt.tight_layout()
    plt.show()


def show_points(driver_df: pd.DataFrame):
    print("\nPoints per race:")
    print(driver_df[["round", "race_name", "points"]].to_string(index=False))

    do_plot = input("Show graph? (y/n): ").strip().lower()
    if do_plot != "y":
        return

    want_legend = input("Show legend? (y/n): ").strip().lower() == "y"
    legend_loc = None
    if want_legend:
        print("\nLegend position:")
        print("1 - Upper right")
        print("2 - Upper left")
        print("3 - Lower right")
        print("4 - Lower left")
        print("5 - Best")

        loc_map = {
            "1": "upper right",
            "2": "upper left",
            "3": "lower right",
            "4": "lower left",
            "5": "best",
        }

        while True:
            c = input("Choose legend position (1–5): ").strip()
            if c in loc_map:
                legend_loc = loc_map[c]
                break
            print("Invalid choice, try again.")

    plt.figure(figsize=(11, 5))

    bars = plt.bar(driver_df["round"], driver_df["points"], label="Points")

    plt.xlabel("Round")
    plt.ylabel("Points")
    plt.title(f"{driver_df['driver_name'].iloc[0]} – Points per race")

    plt.xticks(driver_df["round"])
    plt.grid(True, which="both", axis="both", linestyle="--", alpha=0.5)

    plt.ylim(0, 28)
    plt.yticks(range(0, 26, 5))

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.3,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    if want_legend:
        plt.legend(loc=legend_loc)

    plt.tight_layout()
    plt.show()


def show_cumulative(driver_df: pd.DataFrame):
    print("\nCumulative points:")
    print(driver_df[["round", "race_name", "cumulative_points"]].to_string(index=False))

    do_plot = input("Show graph? (y/n): ").strip().lower()
    if do_plot != "y":
        return

    want_legend = input("Show legend? (y/n): ").strip().lower() == "y"
    legend_loc = None
    if want_legend:
        print("\nLegend position:")
        print("1 - Upper right")
        print("2 - Upper left")
        print("3 - Lower right")
        print("4 - Lower left")
        print("5 - Best")

        loc_map = {
            "1": "upper right",
            "2": "upper left",
            "3": "lower right",
            "4": "lower left",
            "5": "best",
        }

        while True:
            c = input("Choose legend position (1–5): ").strip()
            if c in loc_map:
                legend_loc = loc_map[c]
                break
            print("Invalid choice, try again.")

    rounds = driver_df["round"]
    cum = driver_df["cumulative_points"]

    max_points = float(cum.max())
    y_max = max_points + max(10, max_points * 0.06)

    plt.figure(figsize=(11, 5))

    plt.plot(
        rounds,
        cum,
        marker="o",
        markersize=4,
        linewidth=2,
        label="Cumulative points",
    )

    prev = 0
    last_round = int(rounds.iloc[-1])

    for r, val in zip(rounds, cum):
        if val > prev or r == last_round:
            plt.text(
                r,
                val + max_points * 0.01,
                f"{int(val)}",
                ha="center",
                va="bottom",
                fontsize=9,
            )
        prev = val

    plt.xlabel("Round")
    plt.ylabel("Cumulative points")
    plt.title(f"{driver_df['driver_name'].iloc[0]} – Cumulative points")

    plt.xticks(rounds)
    plt.ylim(0, y_max)
    plt.grid(True, which="both", axis="both", linestyle="--", alpha=0.5)

    if want_legend:
        plt.legend(loc=legend_loc)

    plt.tight_layout()
    plt.show()
