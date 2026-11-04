import json
from collections import Counter

# Production countries we treat as "European" (this is a rule, not perfect truth)
EUROPE = {"GB", "FR", "DE", "IT", "ES", "BE", "AT", "NL", "SE", "DK", "NO", "FI",
          "PL", "IE", "CH", "PT", "CZ", "HU", "GR", "RO", "RU", "UA", "TR"}

# Mood words that say little about a story. We'll refine this list after looking
# at the most common keywords printed below.
NOISE_KEYWORDS = {
    # mood words (say little about the story)
    "audacious", "enthusiastic", "admiring", "amused", "suspenseful", "tense",
    "dramatic", "exciting", "playful", "inspirational", "sentimental", "melodramatic",
    "defiant", "hopeful", "optimistic", "powerful", "bold", "intense", "joyful",
    "excited", "lighthearted",
    # production metadata (not about the story)
    "duringcreditsstinger", "aftercreditsstinger", "woman director",
    "sequel", "remake",
}


def cinema_tags(movie):
    """Which cinema-type filters does this movie belong to?"""
    lang = movie["language"]
    countries = set(movie["countries"])
    tags = []
    if lang == "hi":
        tags.append("Bollywood")
    if lang in {"ta", "te", "ml", "kn"}:
        tags.append("South Indian")
    if lang == "ko":
        tags.append("Korean")
    if lang == "ja":
        tags.append("Japanese")
    if lang == "en" and "US" in countries:
        tags.append("Hollywood")
    if countries & EUROPE:       # & means "any overlap"
        tags.append("European")
    return tags


def clean_keywords(keywords):
    """Lowercase, remove noise and duplicates, keep the original order."""
    seen = set()
    result = []
    for k in keywords:
        k = k.strip().lower()
        if k and k not in NOISE_KEYWORDS and k not in seen:
            seen.add(k)
            result.append(k)
    return result


def build_text(movie, keywords):
    """The single text description the embedding model will read."""
    parts = []
    if movie["genres"]:
        parts.append("Genres: " + ", ".join(movie["genres"]) + ".")
    if keywords:
        parts.append("Themes: " + ", ".join(keywords) + ".")
    if movie["overview"]:
        parts.append(movie["overview"])
    return " ".join(parts)


with open("data/movies.json", encoding="utf-8") as f:
    raw_movies = json.load(f)

clean = []
seen_ids = set()
for m in raw_movies:
    if m["id"] in seen_ids:          # skip duplicates
        continue
    seen_ids.add(m["id"])

    keywords = clean_keywords(m["keywords"])
    year = int(m["release_date"][:4]) if m["release_date"] else None

    clean.append({
        **m,                          # keep all original fields
        "keywords": keywords,
        "year": year,
        "cinema_tags": cinema_tags(m),
        "text": build_text(m, keywords),
    })

with open("data/movies_clean.json", "w", encoding="utf-8") as f:
    json.dump(clean, f, ensure_ascii=False)

# ---- summary ----
print("Saved", len(clean), "movies to data/movies_clean.json\n")

tag_counts = Counter(tag for m in clean for tag in m["cinema_tags"])
print("Movies per cinema tag:", dict(tag_counts))
print("Movies with no tag at all:", sum(1 for m in clean if not m["cinema_tags"]))
print("Movies with no keywords after cleaning:", sum(1 for m in clean if not m["keywords"]))
print("Movies with no release year:", sum(1 for m in clean if m["year"] is None))

lengths = [len(m["text"]) for m in clean]
print("Average text length:", round(sum(lengths) / len(lengths)), "characters")

print("\nTop 40 keywords (look for vague mood words to add to the noise list):")
top = Counter(k for m in clean for k in m["keywords"]).most_common(40)
print(", ".join(f"{k} ({c})" for k, c in top))

print("\nExample text:\n", clean[0]["title"], "->", clean[0]["text"][:400])