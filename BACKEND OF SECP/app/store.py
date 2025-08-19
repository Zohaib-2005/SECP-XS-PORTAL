import orjson, os
import redis
from .config import settings

r = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=False)

def load_json(path: str):
    with open(path, "rb") as f:
        return orjson.loads(f.read())

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
KEYWORD_MAP = load_json(os.path.join(DATA_DIR, "keyword_map.json"))
TAXONOMY = load_json(os.path.join(DATA_DIR, "taxonomy.json"))
IDS = load_json(os.path.join(DATA_DIR, "masked_dataset_ids.json"))
