from src.llm.vector_store import VectorStore

def test_vector_store_search():
    vs = VectorStore()
    
    queries = [
        "институт",
        "адрес общежития",
        "стоимость проживания",
        "документы для заселения",
        "интернет в общежитии",
        "как приготовить борщ",
        "комендантский час",
        "правила проживания",
        "столовая",
        "психологическая помощь"
    ]
    
    for q in queries:
        results = vs.similarity_search(q)
        print(f"Запрос: {q}")
        print(f"Найдено документов: {len(results)}")
        for i, doc in enumerate(results):
            # Поддержка как Document (langchain), так и словарей
            content = getattr(doc, 'page_content', str(doc))[:100]
            print(f"  Док {i+1}: {content}...")
        print()
        # Проверка: результат должен быть списком (может быть пустым)
        assert isinstance(results, list)

if __name__ == "__main__":
    test_vector_store_search()

