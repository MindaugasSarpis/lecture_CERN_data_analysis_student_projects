# Movie Recommendation System

A collaborative filtering-based movie recommender built with Python and the MovieLens dataset. This program analyzes user rating patterns to find similar movies and suggest what you might enjoy next.

## What It Does

The system works with two CSV files:
- `movies.csv` - movie titles and their genres  
- `ratings.csv` - user ratings data  

From these files, I build a user-movie matrix and calculate cosine similarity scores. Movies with similar rating patterns get higher similarity scores, which drives the recommendations.

## Main Features

**1. Movie-Based Recommendations**

Type in a movie you like, and the system finds similar ones based on how users rated them. You don't need the exact title - partial matches work fine. Each recommendation comes with its genres and a similarity score.

**Example:**
```
Input: "Toy Story"
Output:
                                        title                                       genres  similarity_score
1                         Toy Story 2 (1999)  Adventure|Animation|Children|Comedy|Fantasy          0.572601
2                       Jurassic Park (1993)             Action|Adventure|Sci-Fi|Thriller          0.565637
3       Independence Day (a.k.a. ID4) (1996)             Action|Adventure|Sci-Fi|Thriller          0.564262
4  Star Wars: Episode IV - A New Hope (1977)                      Action|Adventure|Sci-Fi          0.557388
5                        Forrest Gump (1994)                     Comedy|Drama|Romance|War          0.547096
```

**2. Random Movie Pick**

Not sure what to watch? Get a random movie from the dataset. You can then see similar movies if you're interested.

**Example:**
```
🎬 Random Movie: Shawshank Redemption, The (1994)
📁 Genres: Crime|Drama
Would you like to see similar movies? (yes/no):
```

**3. User-Based Recommendations**

This feature finds similar users and predicts what movies you'd rate highly based on their preferences. Note: This requires a user ID, so it's mainly included for demonstration purposes rather than practical use.

## Tech Stack

- Python 3
- Pandas (data handling)
- NumPy (numerical operations)
- scikit-learn (cosine similarity calculations)
- MovieLens dataset

## Installation

Before running the program, you need to install the required Python libraries:

```bash
pip install pandas numpy scikit-learn
```

If you're using pip3:
```bash
pip3 install pandas numpy scikit-learn
```

Make sure you also have the MovieLens dataset files (`movies.csv` and `ratings.csv`) in the same directory as your script.

## How the Algorithm Works

### User-Movie Matrix Construction

The program first creates a matrix where rows are users and columns are movies, with ratings as values. Empty cells (movies a user hasn't rated) get filled with zeros for the similarity calculations.

**Matrix Structure:**
```
            Movie1  Movie2  Movie3  Movie4
User1         5.0     0.0     4.0     0.0
User2         4.0     3.0     0.0     5.0
User3         0.0     4.0     5.0     3.0
```

### Cosine Similarity

Cosine similarity measures how similar two items are by calculating the cosine of the angle between their rating vectors. The result ranges from 0 to 1:
- **1.0** = identical rating patterns
- **0.5** = moderately similar
- **0.0** = completely different patterns

Movies with similar rating patterns across users end up with high similarity scores. When you ask for recommendations, it looks up the most similar movies and returns them ranked by score.

### Collaborative Filtering Process

For user-based recommendations, the same process happens but comparing users instead of movies. It finds users with similar rating patterns and predicts what you'd rate based on what they liked using a weighted average approach.

## Key Functions

### `get_random_movie()`
Returns a randomly selected movie from the dataset along with its title and genres.

**Returns:** `(title, genres)` tuple

### `get_movie_recommendations(movie_title, num_recommendations=5)`
Finds movies similar to the input movie based on collaborative filtering.

**Parameters:**
- `movie_title` (str): The movie to find recommendations for (partial matching supported)
- `num_recommendations` (int): Number of recommendations to return (default: 5)

**Returns:** DataFrame with columns: `title`, `genres`, `similarity_score`

### `get_user_recommendations(user_id, num_recommendations=5)`
Predicts movies a specific user would enjoy based on similar users' preferences.

**Parameters:**
- `user_id` (int): The user ID to generate recommendations for
- `num_recommendations` (int): Number of recommendations to return (default: 5)

**Returns:** DataFrame with columns: `title`, `genres`, `predicted_rating`

## Running the Program

Just run:
```bash
python project.py
```

The program will load the data, show some examples, then give you an interactive menu where you can search for movies or get random suggestions.

### Interactive Menu Options

```
Choose an option:
1. Enter a movie title to get recommendations
2. Get a random movie suggestion
3. Quit
```

## Dataset Requirements

This project uses the MovieLens dataset. Ensure you have these files in the same directory:
- `movies.csv` - Contains `movieId`, `title`, and `genres` columns
- `ratings.csv` - Contains `userId`, `movieId`, and `rating` columns