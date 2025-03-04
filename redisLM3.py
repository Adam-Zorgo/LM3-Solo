import redis
import numpy as np

# Connect to Redis (Make sure Redis server is running)
r = redis.Redis(host='localhost', port=6379, decode_responses=False)

# Function to calculate cosine similarity
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Clear previous data in Redis
r.flushall()

# Cat data (attributes: obedience, agility, appetite)
cats = {
    "Explorer": np.array([0.7, 0.6, 0.4], dtype=np.float32),
    "Alpha": np.array([0.8, 0.3, 0.6], dtype=np.float32),
    "Yoda": np.array([0.6, 0.8, 0.5], dtype=np.float32)
}

# Add cat data to Redis
for cat_name, vector in cats.items():
    r.set(f"cat:{cat_name}", vector.tobytes())  # Store as bytes
    print(f"Added cat: {cat_name} with vector: {vector}")

# Query vector (the target cat attributes to compare with)
query_vector = np.array([0.7, 0.5, 0.6], dtype=np.float32)
print(f"\nQuery Vector: {query_vector}")

# Manual similarity search
results = []
for cat_name, vector in cats.items():
    stored_vector = np.frombuffer(r.get(f"cat:{cat_name}"), dtype=np.float32)
    similarity = cosine_similarity(query_vector, stored_vector)
    results.append((cat_name, similarity))

# Sort results based on similarity score
results.sort(key=lambda x: x[1], reverse=True)

# Display results
print("\nSimilarity Search Results:")
for cat_name, similarity in results:
    print(f"Cat: {cat_name}, Similarity: {similarity:.4f}")
