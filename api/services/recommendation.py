import requests

API_KEY = "ВАШ_API_КЛЮЧ"
BASE_URL = "https://api.themoviedb.org/3"

def get_genre_id(genre_name):
    """Соответствие названия жанра с ID TMDb."""
    genre_mapping = {
        "Комедия": 35,
        "Драма": 18,
        "Фантастика": 878,
        "Ужасы": 27,
        "Боевик": 28,
        "Мелодрама": 10749,
        "Аниме": 16,
    }
    return genre_mapping.get(genre_name)


def get_recommendations(genres, actors):
    """Получить рекомендации фильмов."""
    genre_ids = [get_genre_id(genre) for genre in genres if get_genre_id(genre)]
    genre_ids = ",".join(map(str, genre_ids))

    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "language": "ru-RU",
        "with_genres": genre_ids,
        "sort_by": "popularity.desc",
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])
