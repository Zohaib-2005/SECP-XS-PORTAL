from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import orjson, time
from .store import r, KEYWORD_MAP, TAXONOMY, IDS
from .embedding import normalize, embed, ann_examples
from .config import settings
from .llm_client import classify_with_llm
from collections import Counter

app = FastAPI(title="SECP Walk-Through Backend")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Req(BaseModel):
    complaint_text: str

def cache_get(key: str):
    v = r.get(key)
    return orjson.loads(v) if v else None

def cache_set(key: str, obj: dict, ttl=86400):
    r.setex(key, ttl, orjson.dumps(obj))

def keyword_fast_path(text: str):
    tokens = text.split()[:64]
    hits = [KEYWORD_MAP[t] for t in tokens if t in KEYWORD_MAP]
    if hits:
        most = Counter(orjson.dumps(h).decode() for h in hits).most_common(1)[0][0]
        return orjson.loads(most)
    return None

@app.post("/classify")
async def classify(req: Req):
    t0 = time.time()
    text = normalize(req.complaint_text)
    ck = "class:" + str(hash(text))

    cached = cache_get(ck)
    if cached:
        cached["latency_ms"] = int((time.time()-t0)*1000)
        return cached

    direct = keyword_fast_path(text)
    if direct:
        result = {
            "category": direct["cat"],
            "sub_category": direct["sub"],
            "nature_of_issue": direct["nature"],
            "source": "keyword"
        }
        cache_set(ck, result)
        result["latency_ms"] = int((time.time()-t0)*1000)
        return result

    qvec = embed(text)
    ids, dists = ann_examples(qvec, settings.k_examples)
    examples = []
    for i in ids:
        row = IDS[str(i)]
        examples.append({"text": row["text"], "label": row["label"]})

    try:
        result = await classify_with_llm(text, examples, TAXONOMY)
        result["source"] = "llm"
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    cache_set(ck, result)
    result["latency_ms"] = int((time.time()-t0)*1000)
    return result

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Welcome to SECP Walk-Through Backend API"}
