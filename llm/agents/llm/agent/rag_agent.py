# llm/agent/rag_agent.py
from llm.client import LLMClient
from utils.config import API_KEY_RAG, RAG_AGENT_CONFIG
from llm.prompt.rag_prompt import SYSTEM_PROMPT
from src.database.retriever import retrieve_context

class RagAgent:
    def __init__(self):
        if not API_KEY_RAG:
            raise ValueError("YANDEX_CLOUD_API_KEY_2 не задан в .env")
        self.llm = LLMClient(API_KEY_RAG)

    async def generate(self, user_query: str) -> str:
        context = retrieve_context(user_query)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Контекст:\n{context}\n\nВопрос:\n{user_query}"}
        ]
        return await self.llm.generate_response(messages, **RAG_AGENT_CONFIG)
