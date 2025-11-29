import requests
import os
from dotenv import load_dotenv
from config.llm_config import LLM_CONFIG

load_dotenv()

CLOUD_API_KEY = os.getenv("CLOUD_API_KEY")
GENERATE_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

def generate_response(prompt: str) -> str:
    headers = {
        "Authorization": f"Api-Key {CLOUD_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": LLM_CONFIG["model_uri"],
        "completionOptions": {
            "temperature": LLM_CONFIG["temperature"],
            "maxTokens": LLM_CONFIG["max_tokens"]
        },
        "messages": [
            {"role": "system", "text": open("prompts/system_prompt.txt").read()},
            {"role": "user", "text": prompt}
        ]
    }
    response = requests.post(GENERATE_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["result"]["alternatives"][0]["message"]["text"]
