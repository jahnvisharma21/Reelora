import os
import sys
import json
import time

from explore_details import tmdb_get, clean_movie, get_movie_details

TEST_MODE = "--test" in sys.argv  # run with: python collect_movies.py --test

# language code -> how many movies we want
TARGETS = {
    "hi": 400,  # Hindi (Bollywood)
    "ta": 200, "te": 200, "ml": 150, "kn": 100,  # South Indian
    "ko": 300,  # Korean
    "ja": 200,  # Japanese
    "en": 800,  # English (Hollywood and others)
    "fr": 200, "de": 150, "es": 200, "it": 150,  # European
}
if TEST_MODE:
    TARGETS = {lang: 20 for lang in TARGETS}


def discover_ids(language, target):
    """Collect up to `target` movie IDs for one original language."""
    ids = []
    page = 1
    while len(ids) < target:
        data = tmdb_get("/discover/movie", params={
            "with_original_language": language,
            "sort_by": "vote_count.desc",
            "vote_count.gte": 50,
            "include_adult": "false",
            "page": page,
        })
        ids += [m["id"] for m in data["results"]]
        if page >= data["total_pages"]:   # no more pages available
            break
        page += 1
        time.sleep(0.05)                  # be polite to TMDB
    return ids[:target]


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    output_file = "data/movies_test.json" if TEST_MODE else "data/movies.json"

    # 1) collect IDs
    all_ids = []
    for language, target in TARGETS.items():
        ids = discover_ids(language, target)
        print(f"{language}: found {len(ids)} ids (wanted {target})")
        all_ids += ids

    all_ids = list(dict.fromkeys(all_ids))   # remove duplicates, keep order
    print("\nUnique movie ids:", len(all_ids))

    # 2) fetch full details for each
    movies = []
    for i, movie_id in enumerate(all_ids, start=1):
        try:
            movies.append(clean_movie(get_movie_details(movie_id)))
        except Exception as error:
            print(f"skipped {movie_id}: {type(error).__name__}")
        if i % 25 == 0:
            print(f"  {i}/{len(all_ids)} done")
        time.sleep(0.05)

    # 3) save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False)
    print(f"\nSaved {len(movies)} movies to {output_file}")