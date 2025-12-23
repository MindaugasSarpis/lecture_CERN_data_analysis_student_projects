from typing import Tuple

from .config import SEASON_FILES
from .data_io import get_season_results
from .analysis import get_driver_season, get_season_champion
from .plots import show_positions, show_points, show_cumulative


def choose_driver(season_df) -> Tuple[str, str]:
    drivers = (
        season_df[["driver_code", "driver_name"]]
        .drop_duplicates()
        .sort_values("driver_name")
        .reset_index(drop=True)
    )

    print("\nAvailable drivers in that season:")
    for idx, row in drivers.iterrows():
        print(f"{idx + 1:2d}. {row['driver_name']}")

    while True:
        choice = input("\nChoose driver by number: ").strip()
        if not choice.isdigit():
            print("Please enter a number.")
            continue
        i = int(choice) - 1
        if not (0 <= i < len(drivers)):
            print("Number out of range, try again.")
            continue
        break

    return drivers.loc[i, "driver_code"], drivers.loc[i, "driver_name"]


def show_summary(driver_df):
    wins = (driver_df["position"] == 1).sum()
    podiums = (driver_df["position"] <= 3).sum()
    dnfs = (driver_df["position"] == 99).sum()
    total_points = driver_df["points"].sum()

    finished = driver_df[driver_df["position"] < 99]

    avg_pos = finished["position"].mean() if not finished.empty else None
    best_pos = finished["position"].min() if not finished.empty else None

    worst_pos = "DNF" if dnfs > 0 else f"P{int(finished['position'].max())}"

    print("\n=== Summary ===")
    print(f"Wins: {wins}")
    print(f"Podiums: {podiums}")
    print(f"DNFs: {dnfs}")
    print(f"Total points: {total_points:.1f}")

    if avg_pos is not None:
        print(f"Average finish position (excluding DNFs): {avg_pos:.2f}")
        print(f"Best finish position: P{int(best_pos)}")
    else:
        print("Average finish position (excluding DNFs): N/A")
        print("Best finish position: N/A")

    print(f"Worst finish position: {worst_pos}")

    print("\n0 - Back")
    while True:
        choice = input("Your choice: ").strip()
        if choice == "0":
            return
        print("Invalid choice. Press 0 to go back.")


def show_race_result(driver_df):
    races = driver_df.sort_values("round").reset_index(drop=True)

    print("\nRaces:")
    for i, row in races.iterrows():
        print(f"{i + 1:2d}. Round {int(row['round'])} - {row['race_name']}")

    while True:
        choice = input("\nChoose race by number (0 = Back): ").strip()
        if choice == "0":
            return
        if not choice.isdigit():
            print("Please enter a number.")
            continue

        idx = int(choice) - 1
        if not (0 <= idx < len(races)):
            print("Number out of range.")
            continue
        break

    row = races.iloc[idx]

    pos = row["position"]
    pos_str = "DNF" if pos == 99 else f"P{int(pos)}"

    print("\n=== Race result ===")
    print(f"Race:     {row['race_name']}")
    print(f"Round:    {int(row['round'])}")
    print(f"Position: {pos_str}")
    print(f"Points:   {row['points']}")
    print(f"Time:     {row['status']}")

    print("\n0 - Back")
    while True:
        if input("Your choice: ").strip() == "0":
            return
        print("Invalid choice. Press 0 to go back.")


def main():
    print("=== F1 Driver Season Analyzer (CSV 2020–2025) ===")

    # Choose season
    while True:
        season_str = input(f"Enter season {sorted(SEASON_FILES.keys())}: ").strip()
        if not season_str.isdigit():
            print("Season must be a number.")
            continue
        season = int(season_str)
        if season not in SEASON_FILES:
            print("Supported seasons:", ", ".join(map(str, sorted(SEASON_FILES.keys()))))
            continue
        break

    season_df = get_season_results(season)
    if season_df.empty:
        return

    champ_name, champ_code, champ_points = get_season_champion(season_df)

    print(
        f"\nSeason champion {season}: "
        f"{champ_name} - {champ_points:.1f} points\n"
    )

    driver_code, _ = choose_driver(season_df)
    driver_df = get_driver_season(season_df, driver_code)

    while True:
        print("\nCurrent season:", season)
        print("Current driver:", driver_df["driver_name"].iloc[0])

        print("\nChoose action:")
        print("1 - Analyze this driver (stats menu)")
        print("2 - Change driver")
        print("3 - Change season")
        print("0 - Exit")

        action = input("Your choice: ").strip()

        if action == "0":
            print("Goodbye!")
            return

        elif action == "1":
            while True:
                print("\nChoose stat:")
                print("1 - Finishing position per race")
                print("2 - Points per race")
                print("3 - Cumulative points")
                print("4 - Summary (wins, podiums, DNFs, total points)")
                print("5 - Result in a specific race")
                print("0 - Back")

                choice = input("Your choice: ").strip()

                if choice == "0":
                    break
                elif choice == "1":
                    show_positions(driver_df)
                elif choice == "2":
                    show_points(driver_df)
                elif choice == "3":
                    show_cumulative(driver_df)
                elif choice == "4":
                    show_summary(driver_df)
                elif choice == "5":
                    show_race_result(driver_df)
                else:
                    print("Invalid choice, try again.")

        elif action == "2":
            driver_code, _ = choose_driver(season_df)
            driver_df = get_driver_season(season_df, driver_code)

        elif action == "3":
            while True:
                season_str = input(f"Enter season {sorted(SEASON_FILES.keys())}: ").strip()
                if not season_str.isdigit():
                    print("Season must be a number.")
                    continue
                new_season = int(season_str)
                if new_season not in SEASON_FILES:
                    print("Supported seasons:", ", ".join(map(str, sorted(SEASON_FILES.keys()))))
                    continue
                break

            season = new_season
            season_df = get_season_results(season)
            if season_df.empty:
                return
            driver_code, _ = choose_driver(season_df)
            driver_df = get_driver_season(season_df, driver_code)

        else:
            print("Invalid choice, try again.")
