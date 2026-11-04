import json
import time

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

with open("data/movies_clean.json", encoding="utf-8") as f:
    movies = json.load(f)

texts = [m["text"] for m in movies]
print("Movies to embed:", len(texts))

print("Loading model (first run downloads it, about 90 MB)...")
model = SentenceTransformer(MODEL_NAME)

start = time.time()
embeddings = model.encode(
    texts,
    batch_size=64,
    show_progress_bar=True,
    normalize_embeddings=True,   # makes cosine similarity = dot product
)
print(f"Done in {time.time() - start:.0f} seconds")

np.save("data/embeddings.npy", embeddings)

print("Embedding matrix shape:", embeddings.shape)
print("Length of first vector (should be ~1):", float(np.linalg.norm(embeddings[0])))
print("First 5 numbers of the first movie's vector:", embeddings[0][:5])