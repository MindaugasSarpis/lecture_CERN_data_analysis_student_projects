import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics.pairwise import cosine_similarity

# Load the data
print("Loading data...")
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

print(f"Loaded {len(movies)} movies and {len(ratings)} ratings")

# Create user-movie matrix
user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating')
user_movie_matrix_filled = user_movie_matrix.fillna(0)

# Calculate movie similarity
print("\nCalculating movie similarities...")
movie_similarity = cosine_similarity(user_movie_matrix_filled.T)
movie_similarity_df = pd.DataFrame(movie_similarity,
                                   index=user_movie_matrix.columns,
                                   columns=user_movie_matrix.columns)

# For visualization purposes, let's take a sample of movies (too many movies = cluttered)
# Take 10 RANDOM movies each time for variety
print("\nSelecting 10 random movies for visualization...")

# Get movies that have enough ratings (at least 50 ratings for meaningful similarity)
movie_rating_counts = ratings['movieId'].value_counts()
movies_with_enough_ratings = movie_rating_counts[movie_rating_counts >= 50].index

# Randomly sample 10 movies from those with enough ratings
np.random.seed(None)  # Use None for true randomness each run, or set a number for reproducibility
top_movies = np.random.choice(movies_with_enough_ratings, size=10, replace=False)

# Get movie titles for these movies
movie_titles = []
for movie_id in top_movies:
    title = movies[movies['movieId'] == movie_id]['title'].values[0]
    # Shorten long titles for better display
    if len(title) > 30:
        title = title[:27] + '...'
    movie_titles.append(title)

# Filter similarity matrix to only these movies
similarity_subset = movie_similarity_df.loc[top_movies, top_movies]

print(f"\nCreating 3D heatmap for 10 randomly selected movies...")
print("Movies included:")
for i, title in enumerate(movie_titles):
    print(f"  {i}: {title}")

# Prepare data for 3D plot
x_data, y_data = np.meshgrid(range(len(top_movies)), range(len(top_movies)))
x_data = x_data.flatten()
y_data = y_data.flatten()
z_data = similarity_subset.values.flatten()

# Create 3D plot
fig = plt.figure(figsize=(16, 12))
ax = fig.add_subplot(111, projection='3d')

# Create the 3D bar plot (heatmap style)
dx = dy = 0.8  # Width of bars
colors = plt.cm.viridis(z_data / z_data.max())  # Color based on similarity score

ax.bar3d(x_data, y_data, np.zeros_like(z_data), dx, dy, z_data, 
         color=colors, alpha=0.8, edgecolor='none')

# Labels and title
ax.set_xlabel('Movie', fontsize=11, labelpad=10)
ax.set_ylabel('Movie', fontsize=11, labelpad=10)
ax.set_zlabel('Similarity Score', fontsize=11, labelpad=10)
ax.set_title('3D Heatmap: Movie Similarity Matrix\n(Top 10 Most-Rated Movies)', 
             fontsize=14, fontweight='bold', pad=20)

# Set tick labels to movie titles
ax.set_xticks(range(len(movie_titles)))
ax.set_yticks(range(len(movie_titles)))
ax.set_xticklabels(movie_titles, rotation=45, ha='right', fontsize=8)
ax.set_yticklabels(movie_titles, fontsize=8)

# Add colorbar
mappable = plt.cm.ScalarMappable(cmap='viridis')
mappable.set_array(z_data)
cbar = plt.colorbar(mappable, ax=ax, shrink=0.5, aspect=5)
cbar.set_label('Similarity Score', rotation=270, labelpad=15)

# Adjust viewing angle
ax.view_init(elev=25, azim=45)

plt.tight_layout()

# Save the figure
plt.savefig('3d_similarity_heatmap.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as '3d_similarity_heatmap.png'")

plt.show()

print("\nDone! Higher bars indicate higher similarity between movies.")
print("The diagonal (where x=y) shows perfect similarity (movies with themselves).")

# Also create a 2D heatmap as a bonus (easier to read)
print("\nCreating bonus 2D heatmap...")
fig2, ax2 = plt.subplots(figsize=(12, 10))

im = ax2.imshow(similarity_subset.values, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)

# Add colorbar
cbar2 = plt.colorbar(im, ax=ax2)
cbar2.set_label('Similarity Score', rotation=270, labelpad=20)

# Set tick labels to movie titles
ax2.set_xticks(range(len(movie_titles)))
ax2.set_yticks(range(len(movie_titles)))
ax2.set_xticklabels(movie_titles, rotation=45, ha='right', fontsize=9)
ax2.set_yticklabels(movie_titles, fontsize=9)

# Labels
ax2.set_xlabel('Movie', fontsize=12)
ax2.set_ylabel('Movie', fontsize=12)
ax2.set_title('2D Heatmap: Movie Similarity Matrix\n(Top 10 Most-Rated Movies)', 
              fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('2d_similarity_heatmap.png', dpi=300, bbox_inches='tight')
print("Bonus 2D heatmap saved as '2d_similarity_heatmap.png'")

plt.show()

print("\nBoth visualizations complete!")