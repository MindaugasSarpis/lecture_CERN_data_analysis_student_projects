import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load the data
print("Loading data...")
movies = pd.read_csv('movies.csv') 
ratings = pd.read_csv('ratings.csv')

print(f"Loaded {len(movies)} movies and {len(ratings)} ratings")
print("\nFirst few movies:")
print(movies.head())

# Create a user-item matrix (users as rows, movies as columns, ratings as values)
user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating')

# Fill NaN values with 0 (means user hasn't rated that movie)
user_movie_matrix_filled = user_movie_matrix.fillna(0)

# Calculate similarity between movies using cosine similarity
print("\nCalculating movie similarities...")
movie_similarity = cosine_similarity(user_movie_matrix_filled.T)
movie_similarity_df = pd.DataFrame(movie_similarity, 
                                   index=user_movie_matrix.columns, 
                                   columns=user_movie_matrix.columns)
# Get a random movie from the dataset, returns the movie title and genres
def get_random_movie():
    random_movie = movies.sample(n=1).iloc[0]
    
    print(f"\n🎬 Random Movie: {random_movie['title']}")
    print(f"📁 Genres: {random_movie['genres']}")
    print(f"🆔 Movie ID: {random_movie['movieId']}")
    
    return random_movie['title'], random_movie['genres']
# Get movie recommendations based on a movie title, uses collaborative filtering approach
def get_movie_recommendations(movie_title, num_recommendations=5):
    # Find the movie ID
    movie_matches = movies[movies['title'].str.contains(movie_title, case=False, na=False, regex=False)]
    
    if len(movie_matches) == 0:
        return "Movie not found! Try another title."
    
    # If multiple matches, use the first one
    movie_id = movie_matches.iloc[0]['movieId']
    movie_full_title = movie_matches.iloc[0]['title']
    
    print(f"\nFinding recommendations for: {movie_full_title}")
    
    # Get similarity scores for this movie
    if movie_id not in movie_similarity_df.index:
        return "Not enough rating data for this movie."
    
    similar_scores = movie_similarity_df[movie_id].sort_values(ascending=False)
    
    # Get top N similar movies (excluding the movie itself)
    top_similar = similar_scores.iloc[1:num_recommendations+1]
    
    # Get movie details
    recommendations = []
    for movie_id, score in top_similar.items():
        movie_info = movies[movies['movieId'] == movie_id].iloc[0]
        recommendations.append({
            'title': movie_info['title'],
            'genres': movie_info['genres'],
            'similarity_score': score
        })
    
    df = pd.DataFrame(recommendations)
    df.index = df.index + 1
    return df
#   Get movie recommendations for a specific user, based on what similar users liked
def get_user_recommendations(user_id, num_recommendations=5):
    if user_id not in user_movie_matrix.index:
        return "User ID not found!"
    
    # Get movies the user hasn't rated yet
    user_ratings = user_movie_matrix.loc[user_id]
    unrated_movies = user_ratings[user_ratings.isna()].index
    
    # Calculate similarity between users
    user_similarity = cosine_similarity(user_movie_matrix_filled)
    user_similarity_df = pd.DataFrame(user_similarity,
                                      index=user_movie_matrix.index,
                                      columns=user_movie_matrix.index)
    
    # Get similar users
    similar_users = user_similarity_df[user_id].sort_values(ascending=False).iloc[1:11]
    
    # Predict ratings for unrated movies based on similar users
    predictions = {}
    for movie_id in unrated_movies:
        weighted_sum = 0
        similarity_sum = 0
        
        for similar_user_id, similarity in similar_users.items():
            if not pd.isna(user_movie_matrix.loc[similar_user_id, movie_id]):
                weighted_sum += similarity * user_movie_matrix.loc[similar_user_id, movie_id]
                similarity_sum += similarity
        
        if similarity_sum > 0:
            predictions[movie_id] = weighted_sum / similarity_sum
    
    # Get top recommendations
    top_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:num_recommendations]
    
    recommendations = []
    for movie_id, predicted_rating in top_predictions:
        movie_info = movies[movies['movieId'] == movie_id].iloc[0]
        recommendations.append({
            'title': movie_info['title'],
            'genres': movie_info['genres'],
            'predicted_rating': predicted_rating
        })
    
    df = pd.DataFrame(recommendations)
    df.index = df.index + 1
    return df

# Example usage
print("\n" + "="*60)
print("MOVIE-BASED RECOMMENDATIONS")
print("="*60)
recommendations = get_movie_recommendations("Toy Story", num_recommendations=5)
print(recommendations)

print("\n" + "="*60)
print("USER-BASED RECOMMENDATIONS")
print("="*60)
user_recs = get_user_recommendations(user_id=1, num_recommendations=5)
print(user_recs)

# Interactive section
print("\n" + "="*60)
print("TRY IT YOURSELF!")
print("="*60)
print("\nChoose an option:")
print("1. Enter a movie title to get recommendations")
print("2. Get a random movie suggestion")
print("3. Quit")

while True:
    choice = input("\nYour choice (1/2/3): ").strip()
    
    if choice == '1':
        movie_input = input("Movie title: ").strip()
        result = get_movie_recommendations(movie_input, num_recommendations=5)
        print("\n", result)
    
    elif choice == '2':
        movie_title, genres = get_random_movie()
        
        # Ask if user wants recommendations for this random movie
        get_recs = input("\nWould you like to see similar movies? (yes/no): ").strip().lower()
        if get_recs in ['yes', 'y']:
            result = get_movie_recommendations(movie_title, num_recommendations=5)
            print("\n", result)
    
    elif choice == '3':
        print("Thanks for using the movie recommender :)")
        break
    
    else:

        print("Invalid choice. Please enter 1, 2, or 3.")
