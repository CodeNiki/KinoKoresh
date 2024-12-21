import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import ast

app = FastAPI()

# Загрузка данных
movies = pd.read_csv('../tests/movies_metadata.csv', low_memory=False)
credits = pd.read_csv('../tests/credits.csv')

# Обработка данных
movies = movies[['id', 'title', 'genres', 'overview', 'popularity']].dropna()
credits = credits[['id', 'cast', 'crew']].dropna()
movies['id'] = movies['id'].astype(str)
credits['id'] = credits['id'].astype(str)
movies = movies.merge(credits, on='id')

# Функции для парсинга
def parse_genres(genres):
    try:
        genres_list = ast.literal_eval(genres)
        return " ".join([g['name'] for g in genres_list])
    except:
        return ""

def parse_cast(cast, top_n=5):
    try:
        cast_list = ast.literal_eval(cast)
        return " ".join([member['name'] for member in cast_list[:top_n]])
    except:
        return ""

def parse_crew(crew, job):
    try:
        crew_list = ast.literal_eval(crew)
        return " ".join([person['name'] for person in crew_list if person['job'] == job])
    except:
        return ""

movies['genres_processed'] = movies['genres'].apply(parse_genres)
movies['director'] = movies['crew'].apply(lambda x: parse_crew(x, 'Director'))
movies['actors'] = movies['cast'].apply(parse_cast)
movies['metadata'] = (
        movies['genres_processed'] + " " +
        movies['director'] + " " +
        movies['actors'] + " " +
        movies['overview'].fillna("")
)

# Создание TF-IDF матрицы
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['metadata'])

# Настройка модели Nearest Neighbors
nn = NearestNeighbors(metric='cosine', algorithm='brute')
nn.fit(tfidf_matrix)

# Модель данных для запросов
class RecommendationRequest(BaseModel):
    name: str
    surname: str
    age: str
    genres: str
    actors: str
    favorite_movie: str
    num_recommendations: int = 5

def filter_recommendations_by_genres_and_actors(recommendations, genres, actors):
    filtered = []
    genre_set = set(genres.lower().split(","))
    actor_set = set(actors.lower().split(","))

    for movie in recommendations:
        movie_genres = set(movie['genres_processed'].lower().split())
        movie_actors = set(movie['actors'].lower().split())
        if genre_set.intersection(movie_genres) or actor_set.intersection(movie_actors):
            filtered.append(movie)

    return filtered if filtered else recommendations

def get_recommendations(title, genres, actors, num_recommendations=5):
    query_index = movies[movies['title'].str.contains(title, case=False, na=False)].index
    if query_index.empty:
        return []

    query_vector = tfidf_matrix[query_index]
    distances, indices = nn.kneighbors(query_vector, n_neighbors=num_recommendations + 10)
    recommendations_indices = indices[0][1:]
    raw_recommendations = movies.iloc[recommendations_indices][
        ['title', 'genres_processed', 'director', 'actors']].to_dict(orient='records')

    return filter_recommendations_by_genres_and_actors(raw_recommendations, genres, actors)[:num_recommendations]

def get_basic_recommendations(num_recommendations=5):
    sorted_movies = movies.sort_values(by='popularity', ascending=False)
    return sorted_movies[['title', 'genres_processed', 'director', 'actors']].head(num_recommendations).to_dict(orient='records')

@app.post("/recommendations")
def recommend_movies(request: RecommendationRequest):
    recommendations = get_recommendations(
        title=request.favorite_movie,
        genres=request.genres,
        actors=request.actors,
        num_recommendations=request.num_recommendations
    )

    if not recommendations:
        return {"status": "error", "message": "No recommendations found."}

    return {"status": "success", "recommendations": recommendations}

@app.get("/basic_recommendations")
def basic_recommend_movies():
    recommendations = get_basic_recommendations(num_recommendations=5)
    return {"status": "success", "recommendations": recommendations}