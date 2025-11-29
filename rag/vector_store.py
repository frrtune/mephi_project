import requests
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
VECTOR_SEARCH_URL = "https://your-vector-search-endpoint.cloud.yandex.net/search"  # ← замените!

def search_similar(embedding: List[float], top_k: int = 3) -> List[Dict]:
    headers = {
        "Authorization": f"Api-Key {CLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "vector": embedding,
        "top_k": top_k
    }
    response = requests.post(VECTOR_SEARCH_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["results"]  # предполагаем формат: [{"text": "...", "score": 0.9}]
