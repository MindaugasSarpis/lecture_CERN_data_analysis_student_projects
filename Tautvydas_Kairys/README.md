# Movie Recommendation System

This project implements a movie recommendation system using collaborative filtering techniques and the MovieLens dataset. The system analyzes user ratings to identify similarities between movies and between users, ultimately providing personalized movie suggestions.

## Overview

The program loads two datasets:

- **movies.csv** – contains movie titles and genres  
- **ratings.csv** – contains user ratings for each movie  

Using these files, the script constructs a user–movie ratings matrix and applies cosine similarity to measure how closely movies or users resemble one another. These similarity scores form the basis of the recommendation engine.

## Features

### Movie-Based Recommendations
Given a movie title, the system identifies the most similar movies by comparing rating patterns across all users.
- Supports partial title matching  
- Returns a ranked list of similar films  
- Includes genres and similarity scores for each recommendation  

### User-Based Recommendations (unused)
For a provided user ID, the system predicts which unrated movies the user is likely to enjoy.
- Finds the most similar users  
- Computes weighted average predicted ratings  
- Returns the highest-rated recommendations for that user  

### Random Movie Selection
Users can request a random movie from the dataset and optionally receive recommendations based on that selection.

## Technologies Used
- Python 3  
- Pandas  
- NumPy  
- scikit-learn (for cosine similarity)  
- MovieLens dataset

## How It Works

1. The script loads and processes the movie and rating datasets.  
2. It builds a user–movie matrix and fills missing values with zeros when calculating similarities.  
3. It computes:  
   - movie-to-movie similarity  
   - user-to-user similarity  
4. Based on the selected option, it returns either movie-based or user-based recommendations.  
5. An interactive menu allows the user to enter a movie title, request a random movie, or exit the program.

## Running the Program

Run the following command (or just press run):

```bash
python project.py

