from src.llm.vector_store import VectorStore

def test_vector_store_contains_data():
    vs = VectorStore()
    docs = vs.similarity_search("институт")
    assert isinstance(docs, list)
    assert len(docs) == min(3, len(vs.docs))

def test_vector_store_retrieves_addresses():
    vs = VectorStore()
    docs = vs.similarity_search("адрес общежития")
    assert isinstance(docs, list)
    assert len(docs) > 0
    # Проверяем, что хотя бы в одном документе есть слово "Москва" или "улица"
    assert any("Москва" in doc.page_content or "улица" in doc.page_content for doc in docs)

def test_vector_store_retrieves_costs():
    vs = VectorStore()
    docs = vs.similarity_search("стоимость проживания")
    assert isinstance(docs, list)
    assert len(docs) > 0
    # Проверяем, что хотя бы в одном документе есть "руб" или "рублей"
    assert any("руб" in doc.page_content.lower() for doc in docs)

def test_vector_store_handles_irrelevant_query():
    vs = VectorStore()
    docs = vs.similarity_search("как приготовить борщ")
    # Для нерелевантного запроса может вернуться пустой список или общие документы
    # Проверяем только корректность типа и ограничение по количеству
    assert isinstance(docs, list)
    assert len(docs) <= 3

def test_vector_store_consistency():
    vs = VectorStore()
    # Один и тот же запрос должен возвращать одинаковое количество результатов
    result1 = vs.similarity_search("документы для заселения")
    result2 = vs.similarity_search("документы для заселения")
    assert len(result1) == len(result2)

