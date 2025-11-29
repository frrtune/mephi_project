import os
from dotenv import load_dotenv

load_dotenv()

LLM_CONFIG = {
    "temperature": float(os.getenv("LLM_TEMPERATURE", 0.3)),
    "max_tokens": int(os.getenv("LLM_MAX_TOKENS", 512)),
    "model_uri": f"gpt://{os.getenv('FOLDER_ID')}/yandexgpt/latest"
}
