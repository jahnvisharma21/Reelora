import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TMDB_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "accept": "application/json"}


def get_movie_details(movie_id):
    """Fetch full details, keywords and credits for one movie in a single call."""
    response = requests.get(
        f"{BASE_URL}/movie/{movie_id}",
        headers=HEADERS,
        params={"append_to_response": "keywords,credits"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def clean_movie(raw):
    """Keep only the fields Reelora needs."""
    crew = raw["credits"]["crew"]
    director = next((p["name"] for p in crew if p["job"] == "Director"), None)

    return {
        "id": raw["id"],
        "title": raw["title"],
        "original_title": raw["original_title"],
        "language": raw["original_language"],
        "countries": [c["iso_3166_1"] for c in raw["production_countries"]],
        "release_date": raw["release_date"],
        "runtime": raw["runtime"],
        "overview": raw["overview"],
        "genres": [g["name"] for g in raw["genres"]],
        "keywords": [k["name"] for k in raw["keywords"]["keywords"]],
        "cast": [p["name"] for p in raw["credits"]["cast"][:5]],
        "director": director,
        "rating": raw["vote_average"],
        "votes": raw["vote_count"],
        "poster_path": raw["poster_path"],
    }


# Interstellar's TMDB id is 157336 (as far as I know; the output will confirm)
raw = get_movie_details(157336)

print("Top-level fields TMDB sent us:", len(raw.keys()))
print()

movie = clean_movie(raw)
print(json.dumps(movie, indent=2, ensure_ascii=False))