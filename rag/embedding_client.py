import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")
EMBEDDING_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"

def get_embedding(text: str) -> list[float]:
    headers = {
        "Authorization": f"Api-Key {CLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"emb://{FOLDER_ID}/text-search-doc/v1",
        "inputText": text
    }
    response = requests.post(EMBEDDING_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["embedding"]
