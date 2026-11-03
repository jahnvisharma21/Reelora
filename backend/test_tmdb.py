import os
import requests
from dotenv import load_dotenv

# Read the secrets from the .env file
load_dotenv()
token = os.getenv("TMDB_TOKEN")

if not token:
    print("No token found. Check that backend/.env exists and has TMDB_TOKEN=...")
    raise SystemExit

print("Token loaded. Length:", len(token), "characters")

# Our "library card" goes in the request header
headers = {
    "Authorization": f"Bearer {token}",
    "accept": "application/json",
}

# Ask TMDB to search for a movie
url = "https://api.themoviedb.org/3/search/movie"
response = requests.get(url, headers=headers, params={"query": "Interstellar"}, timeout=15)

print("Status code:", response.status_code)

if response.status_code == 200:
    results = response.json()["results"]
    print("Movies found:", len(results))
    for movie in results[:3]:
        print("-", movie["title"], "|", movie["release_date"])
else:
    print("Something went wrong:", response.text)