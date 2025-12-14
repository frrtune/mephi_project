from src.data.mephi_facts import MEPHI_FACTS

class VectorStore:
    def __init__(self):
        # Загружаем тексты о МИФИ
        self.docs = MEPHI_FACTS

    def similarity_search(self, query: str, k: int = 3):
        # Заглушка: возвращает первые k документов (можно заменить на вычисление эмбеддингов)
        return self.docs[:k]
