import hashlib, numpy as np, orjson, os

# Temporarily disable hnswlib to test the project
# try:
#     import hnswlib  # optional at build time
#     HNSW_AVAILABLE = True
#     print("hnswlib successfully imported!")
# except Exception as e:
#     print(f"hnswlib not available: {e}")
#     HNSW_AVAILABLE = False

# Force disable hnswlib for testing
HNSW_AVAILABLE = False
print("hnswlib functionality disabled for testing")

from .config import settings
from .store import r

INDEX = None
INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "masked_dataset_hnsw.bin")

print(f"Index file exists: {os.path.exists(INDEX_PATH)}")
print(f"Looking for file at: {os.path.abspath(INDEX_PATH)}")

# Temporarily disable hnswlib index loading for testing
# if HNSW_AVAILABLE and os.path.exists(INDEX_PATH):
#     INDEX = hnswlib.Index(space="cosine", dim=settings.embed_dim)
#     INDEX.load_index(INDEX_PATH)
#     INDEX.set_ef(settings.ef_search)

def _sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def normalize(s: str) -> str:
    return " ".join(s.lower().strip().split())[:2000]

def get_cached_embedding(text: str):
    key = f"emb:{_sha(text)}"
    v = r.get(key)
    if v:
        return np.frombuffer(v, dtype="float32")
    return None

def set_cached_embedding(text: str, vec: np.ndarray):
    key = f"emb:{_sha(text)}"
    r.setex(key, 7*86400, vec.astype(np.float32).tobytes())

def get_embedding_from_local_model(text: str) -> np.ndarray:
    # TODO: replace with your embedder; this dummy uses a hash → pseudo-random vector (for scaffolding)
    rng = np.random.default_rng(abs(int(_sha(text), 16)) % (2**32))
    return rng.random(settings.embed_dim, dtype=np.float32)

def embed(text: str):
    v = get_cached_embedding(text)
    if v is not None:
        return v
    v = get_embedding_from_local_model(text)
    set_cached_embedding(text, v)
    return v

def ann_examples(vec, k: int):
    if not HNSW_AVAILABLE:
        print("Warning: hnswlib not available, returning empty results")
        return [], []
    if INDEX is None:
        print("Warning: INDEX not loaded, returning empty results")
        return [], []
    labels, dists = INDEX.knn_query(vec, k=k)
    return labels[0].tolist(), dists[0].tolist()


def complaint_handler(complaint: str):
    # Normalize the complaint text
    normalized_complaint = normalize(complaint)

    # Embed the complaint text
    complaint_vector = embed(normalized_complaint)

    # Find similar complaints in the dataset
    similar_complaints, distances = ann_examples(complaint_vector, k=5)

    return {
        "normalized_complaint": normalized_complaint,
        "complaint_vector": complaint_vector.tolist(),
        "similar_complaints": similar_complaints,
        "distances": distances
    }
