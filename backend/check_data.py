import json
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "data/movies.json"

with open(path, encoding="utf-8") as f:
    movies = json.load(f)

print("File:", path)
print("Total movies:", len(movies))

print("\nMovies per language:")
for language, count in Counter(m["language"] for m in movies).most_common():
    print(f"  {language}: {count}")

print("\nMissing or weak data, by language")
print("(language | movies | no overview | overview < 50 chars | no keywords | no poster | no director)")
languages = sorted(set(m["language"] for m in movies))
for lang in languages:
    group = [m for m in movies if m["language"] == lang]
    no_overview = sum(1 for m in group if not m["overview"])
    short = sum(1 for m in group if m["overview"] and len(m["overview"]) < 50)
    no_keywords = sum(1 for m in group if not m["keywords"])
    no_poster = sum(1 for m in group if not m["poster_path"])
    no_director = sum(1 for m in group if not m["director"])
    print(f"  {lang} | {len(group)} | {no_overview} | {short} | {no_keywords} | {no_poster} | {no_director}")

lengths = [len(m["overview"]) for m in movies if m["overview"]]
print("\nAverage overview length:", round(sum(lengths) / len(lengths)), "characters")

keyword_counts = [len(m["keywords"]) for m in movies]
print("Average keywords per movie:", round(sum(keyword_counts) / len(keyword_counts), 1))

print("\nCountries seen:", Counter(c for m in movies for c in m["countries"]).most_common(12))