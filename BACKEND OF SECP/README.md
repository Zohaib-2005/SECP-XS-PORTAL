# SECP Walk-Through AI Backend (FastAPI)
A production-ready skeleton for the **Walk-Through Window** complaint classifier.
- **FastAPI** server with constant-time bounded logic (cache → keyword → ANN → LLM).
- **Redis** caching, **HNSW** ANN index (hnswlib), structured **LLM** call.
- Dataset is **PII-masked offline**; this repo expects only masked data.

## Quick Start
```bash
# 1) Copy your masked dataset & index (see /scripts/build_index.py)
cp data/* ./data/

# 2) Start services
docker compose up --build

# 3) Test
curl -X POST http://localhost:8000/classify -H "Content-Type: application/json" \
  -d '{"complaint_text": "My health claim is pending and no one is helping"}'
```

## Layout
```
app/
  main.py            # FastAPI app
  llm_client.py      # LLM API wrapper
  embedding.py       # embedding routine + cache
  store.py           # redis & data loaders
  config.py          # settings
data/
  taxonomy.json      # SECP taxonomy (example)
  keyword_map.json   # keyword→label map (example)
  masked_dataset_ids.json # id→{text,label} map (example)
  masked_dataset_hnsw.bin # ANN index (placeholder)
scripts/
  build_index.py     # build HNSW from masked dataset (JSONL/CSV)
Dockerfile
docker-compose.yml
requirements.txt
.env.example
README.md
```

## Notes
- Replace `get_embedding_from_local_model` with your actual embedder or API.
