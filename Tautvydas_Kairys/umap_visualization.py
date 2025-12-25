import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
import umap
import warnings

# Suppress UMAP warnings
warnings.filterwarnings('ignore', message='n_jobs value')

# Load the data
print("Loading data...")
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

print(f"Loaded {len(movies)} movies and {len(ratings)} ratings")

# Create user-movie matrix
user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating')
user_movie_matrix_filled = user_movie_matrix.fillna(0)

# Prepare data for UMAP (movies as rows, users as columns)
movie_features = user_movie_matrix_filled.T

# Get the most common genre for each movie (for coloring)
def get_primary_genre(genres_str):
    """Extract the first/primary genre from the genres string"""
    if pd.isna(genres_str) or genres_str == '(no genres listed)':
        return 'Unknown'
    return genres_str.split('|')[0]

movies['primary_genre'] = movies['genres'].apply(get_primary_genre)

# Filter to only movies that have ratings (exist in our matrix)
movies_with_ratings = movies[movies['movieId'].isin(movie_features.index)]

# Align the genres with the movie features
aligned_genres = movies_with_ratings.set_index('movieId').loc[movie_features.index, 'primary_genre']

print("\nApplying UMAP dimensionality reduction...")
print("This may take a minute...")

# Apply UMAP to reduce to 2D
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
embedding = reducer.fit_transform(movie_features)

print("UMAP complete! Creating visualization...")

# Create the plot
plt.figure(figsize=(14, 10))

# Get unique genres and assign rainbow colors
unique_genres = aligned_genres.unique()
# Use hsv colormap for true rainbow colors
colors = plt.cm.hsv(np.linspace(0, 0.9, len(unique_genres)))  # 0.9 to avoid wrapping back to red
genre_to_color = dict(zip(unique_genres, colors))

# Plot each genre
for genre in unique_genres:
    mask = aligned_genres == genre
    plt.scatter(embedding[mask, 0], embedding[mask, 1], 
               label=genre, alpha=0.7, s=80, 
               c=[genre_to_color[genre]], edgecolors='black', linewidth=0.5)

plt.title('UMAP Projection of Movies by Genre\n(Based on User Rating Patterns)', 
          fontsize=16, fontweight='bold')
plt.xlabel('UMAP Dimension 1', fontsize=12)
plt.ylabel('UMAP Dimension 2', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
plt.tight_layout()
plt.grid(True, alpha=0.3)

# Save the figure
plt.savefig('umap_movie_distribution.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'umap_movie_distribution.png'")

plt.show()

print("\nDone! Movies that are close together have similar rating patterns.")
print("Colors represent the primary genre of each movie.")