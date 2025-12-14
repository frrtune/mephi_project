from src.llm.vector_store import VectorStore

class RAG:
    def __init__(self, llm):
        self.vector_store = VectorStore()
        self.llm = llm

    def generate_answer(self, query: str) -> str:
        contexts = self.vector_store.similarity_search(query, k=2)
        prompt = " ".join(contexts) + f"\n\nВопрос: {query}"
        result = self.llm.generate([{"role": "user", "content": prompt}])
        return result.generations[0][0].text.strip()

