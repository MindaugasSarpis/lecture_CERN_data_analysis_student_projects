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

**2. Random Movie Pick**

Not sure what to watch? Get a random movie from the dataset. You can then see similar movies if you're interested.

**3. User-Based Recommendations**

This feature finds similar users and predicts what movies you'd rate highly based on their preferences. Note: This requires a user ID, so it's mainly included for demonstration purposes rather than practical use.

## Tech Stack

- Python 3
- Pandas (data handling)
- NumPy (numerical operations)
- scikit-learn (cosine similarity calculations)
- MovieLens dataset

## How the Algorithm Works

The program first creates a matrix where rows are users and columns are movies, with ratings as values. Empty cells (movies a user hasn't rated) get filled with zeros for the similarity calculations.

Then it computes cosine similarity between movies. Movies with similar rating patterns across users end up with high similarity scores. When you ask for recommendations, it just looks up the most similar movies and returns them ranked by score.

For user-based recommendations, the same process happens but comparing users instead of movies. It finds users with similar rating patterns and predicts what you'd rate based on what they liked.

## Running It

Just run:
```bash
python project.py
```

The program will load the data, show some examples, then give you an interactive menu where you can search for movies or get random suggestions.
