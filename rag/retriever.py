from .embedding_client import get_embedding
from .vector_store import search_similar

def retrieve_context(query: str, top_k: int = 3) -> str:
    embedding = get_embedding(query)
    results = search_similar(embedding, top_k=top_k)
    # Собираем только тексты
    context = "\n\n".join([r["text"] for r in results if r["score"] > 0.5])
    return context if context else "Контекст не найден."
