import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TMDB_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {TOKEN}", "accept": "application/json"})


def tmdb_get(path, params=None, retries=5):
    """GET a TMDB endpoint. If the connection fails, wait and try again."""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(f"{BASE_URL}{path}", params=params, timeout=15)
            if response.status_code == 429:  # TMDB says: slow down
                time.sleep(2 * attempt)
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            print(f"  attempt {attempt}/{retries} failed: {type(error).__name__}")
            if attempt == retries:
                raise
            time.sleep(2 * attempt)  # wait 2s, 4s, 6s... between tries


def get_movie_details(movie_id):
    """Fetch full details, keywords and credits for one movie in a single call."""
    return tmdb_get(f"/movie/{movie_id}", params={"append_to_response": "keywords,credits"})


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


if __name__ == "__main__":
    raw = get_movie_details(157336)
    print("Top-level fields TMDB sent us:", len(raw.keys()))
    print()
    print(json.dumps(clean_movie(raw), indent=2, ensure_ascii=False))