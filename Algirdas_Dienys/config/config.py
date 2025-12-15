# File where you need to specify the filepaths, filter the dates if you want, 
# check if the name of the columns in your coresponding csv file matches at least
# one in NUT_COLS and HOME_COLS, and set target goals.

# Filepath to nutrition file
NUTRITION_CSV = "data/raw/Nutrition-Summary-2025-10-31-to-2025-11-30.csv"

# Filepath to home time file (optional)
HOME_TIME_CSV = "data/raw/home_time.csv"   # or None

# Filter dates (optional)
START_DATE = "2025-11-10"   # or None
END_DATE   = "2025-11-30"   # or None

# Column names
# If the name used in your file is not present, include it here or change it in your file
NUT_COLS = {
    "date":     ["Date", "Diary Date", "day", "date"],
    "calories": ["Calories", "Calories (kcal)", "Energy (kcal)", "Energy"],
    "carbs":    ["Carbohydrates (g)", "Carbohydrates", "Carbs (g)", "Carbs"],
    "protein":  ["Protein (g)", "Protein"],
    "fat":      ["Fat (g)", "Fat", "Total Fat (g)"],
    "sugar":    ["Sugar", "Sugars (g)", "Sugars"],     # optional, can be []
    "fiber":    ["Fiber", "Fibre", "Dietary Fiber (g)"]# optional, can be []
}

HOME_COLS = {
    "date":      ["Date", "day", "date"],
    "time_home": ["Time at home (hours)", "Time spent at home (hours)", "hours_at_home"]
}

# Nutrition targets
# Edit these targets to your liking
SCORE_TARGETS = {
    "Calories": (2000, 2500),
    "Carb % (net, 4-4-9)": (50, 60),
    "Protein % (4-4-9)":   (15, 25),
    "Fat % (4-4-9)":       (20, 30),
}

# Select where you want your plots and scoring to be sent
OUTDIR = "results"