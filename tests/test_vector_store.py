from src.llm.vector_store import VectorStore

def test_vector_store_contains_data():
    vs = VectorStore()
    docs = vs.similarity_search("институт")
    assert isinstance(docs, list)
    assert len(docs) == min(3, len(vs.docs))

