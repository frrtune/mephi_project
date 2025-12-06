# src/database/retriever.py
import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "mephi_kb"

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    emb_fn = DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=emb_fn
    )

def retrieve_context(query: str, top_k: int = 3) -> str:
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=top_k)
    docs = results.get("documents", [[]])[0]
    return "\n\n".join(docs) if docs else "Контекст не найден."
