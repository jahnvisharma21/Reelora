import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TMDB_TOKEN")
BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "accept": "application/json"}


def discover_movies(language, page=1):
    """Ask TMDB for one page (20 movies) in a given original language."""
    response = requests.get(
        f"{BASE_URL}/discover/movie",
        headers=HEADERS,
        params={
            "with_original_language": language,
            "sort_by": "vote_count.desc",   # most-voted movies first
            "vote_count.gte": 50,           # skip movies with almost no votes
            "include_adult": "false",
            "page": page,
        },
        timeout=15,
    )
    response.raise_for_status()  # stops with a clear error if status is not 200
    return response.json()


# Try Hindi (Bollywood) first
data = discover_movies("hi", page=1)

print("Total Hindi movies matching filters:", data["total_results"])
print("Total pages:", data["total_pages"])
print("Movies on this page:", len(data["results"]))
print()

for movie in data["results"][:10]:
    year = movie["release_date"][:4] if movie.get("release_date") else "????"
    print(f"{movie['title']} ({year}) | lang={movie['original_language']} | votes={movie['vote_count']} | id={movie['id']}")

# Now try Korean to compare
print("\n--- Korean ---")
data_ko = discover_movies("ko", page=1)
print("Total Korean movies matching filters:", data_ko["total_results"])
for movie in data_ko["results"][:5]:
    year = movie["release_date"][:4] if movie.get("release_date") else "????"
    print(f"{movie['title']} ({year}) | votes={movie['vote_count']}")