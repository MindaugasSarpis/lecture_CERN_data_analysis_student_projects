import pandas as pd
import numpy as np
import umap
import plotly.graph_objects as go
import plotly.express as px
import warnings
import re

warnings.filterwarnings('ignore', message='n_jobs value')

# -----------------------
# Load data
# -----------------------
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# -----------------------
# Extract release year
# -----------------------
def extract_year(title):
    match = re.search(r"\((\d{4})\)", str(title))
    return int(match.group(1)) if match else np.nan

movies["release_year"] = movies["title"].apply(extract_year)

# -----------------------
# User–movie matrix
# -----------------------
user_movie_matrix = ratings.pivot_table(
    index="userId",
    columns="movieId",
    values="rating"
).fillna(0)

movie_features = user_movie_matrix.T

# -----------------------
# Rating statistics
# -----------------------
rating_stats = ratings.groupby("movieId").agg(
    avg_rating=("rating", "mean"),
    rating_count=("rating", "count")
)

# -----------------------
# Genres
# -----------------------
def get_primary_genre(genres):
    if pd.isna(genres) or genres == "(no genres listed)":
        return "Unknown"
    return genres.split("|")[0]

movies["primary_genre"] = movies["genres"].apply(get_primary_genre)

# -----------------------
# Align metadata
# -----------------------
movies_aligned = (
    movies
    .set_index("movieId")
    .join(rating_stats)
    .loc[movie_features.index]
)

movies_aligned = movies_aligned.dropna(subset=["release_year"])
movie_features = movie_features.loc[movies_aligned.index]

# -----------------------
# UMAP (3D from ratings)
# -----------------------
reducer = umap.UMAP(
    n_neighbors=15,
    min_dist=0.1,
    n_components=3,
    random_state=42
)

embedding = reducer.fit_transform(movie_features)

# -----------------------
# Plot DataFrame
# -----------------------
plot_df = pd.DataFrame({
    "UMAP_1": embedding[:, 0],
    "UMAP_2": embedding[:, 1],
    "UMAP_3": embedding[:, 2],
    "Release Year": movies_aligned["release_year"].values,
    "Average Rating": movies_aligned["avg_rating"].values,
    "Rating Count": movies_aligned["rating_count"].values,
    "Genre": movies_aligned["primary_genre"].values,
    "Title": movies_aligned["title"].values
})

# -----------------------
# Z-axis options
# -----------------------
z_options = {
    "UMAP Dimension 3 (Rating Similarity)": "UMAP_3",
    "Release Year": "Release Year",
    "Average User Rating": "Average Rating",
    "Number of Ratings (Popularity)": "Rating Count"
}

initial_z_label = "UMAP Dimension 3 (Rating Similarity)"
initial_z_column = z_options[initial_z_label]

# -----------------------
# Colors
# -----------------------
genres = plot_df["Genre"].unique()
colors = px.colors.sample_colorscale(
    "hsv",
    [i / (len(genres) - 1) for i in range(len(genres))]
)

# -----------------------
# Figure
# -----------------------
fig = go.Figure()

for i, genre in enumerate(genres):
    gdf = plot_df[plot_df["Genre"] == genre]

    fig.add_trace(go.Scatter3d(
        x=gdf["UMAP_1"],
        y=gdf["UMAP_2"],
        z=gdf[initial_z_column],
        mode="markers",
        name=genre,
        marker=dict(
            size=5,
            opacity=0.7,
            color=colors[i],
            line=dict(width=0.4, color="white")
        ),
        text=gdf["Title"],
        customdata=np.stack([
            gdf["UMAP_3"],
            gdf["Release Year"],
            gdf["Average Rating"],
            gdf["Rating Count"]
        ], axis=-1),
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Genre: " + genre + "<br>"
            "UMAP 3: %{customdata[0]:.2f}<br>"
            "Release Year: %{customdata[1]}<br>"
            "Avg Rating: %{customdata[2]:.2f}<br>"
            "Ratings Count: %{customdata[3]}<br>"
            "<extra></extra>"
        )
    ))

# -----------------------
# Dropdown menu
# -----------------------
buttons = []

for label, column in z_options.items():
    buttons.append(dict(
        label=label,
        method="update",
        args=[
            {"z": [
                plot_df.loc[plot_df["Genre"] == g, column]
                for g in genres
            ]},
            {"scene.zaxis.title.text": label}
        ]
    ))

# -----------------------
# Layout
# -----------------------
fig.update_layout(
    title=dict(
        text=(
            "3D Movie Similarity Visualization<br>"
            "<sub>X & Y: UMAP (Rating Similarity) | Z: Selectable Movie Attribute</sub>"
        ),
        x=0.5
    ),
    scene=dict(
        xaxis_title="UMAP Dimension 1 (Rating Similarity)",
        yaxis_title="UMAP Dimension 2 (Rating Similarity)",
        zaxis_title=initial_z_label
    ),
    updatemenus=[dict(
        buttons=buttons,
        direction="down",
        x=0.02,
        y=0.98,
        showactive=True
    )],
    width=1200,
    height=800,
    legend=dict(
        bgcolor="rgba(255,255,255,0.85)"
    )
)

fig.write_html("umap_movies_semantic_3d.html")
fig.show()
