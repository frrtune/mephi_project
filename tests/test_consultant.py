# tests/test_consultant.py

import pytest
from src.llm.agents.consultant_agent import RAGConsultantAgent

@pytest.fixture
def consultant_agent():
    """Создаем экземпляр агента для тестов"""
    return RAGConsultantAgent()

def test_address_query(consultant_agent):
    """Тест: вопрос об адресе должен найти информацию в базе"""
    result = consultant_agent.ask_question("Адрес общежития?")
    assert result["answer"] != ""  # Ответ не пустой
    assert result["sources_count"] > 0  # Найдены источники
    assert "общежитие" in result["answer"].lower() or "Москва" in result["answer"]  # Содержит ключевые слова

def test_cost_query(consultant_agent):
    """Тест: вопрос о стоимости должен найти информацию"""
    result = consultant_agent.ask_question("Сколько стоит проживание?")
    assert result["answer"] != ""
    assert result["sources_count"] > 0
    assert "руб" in result["answer"] or "стоимость" in result["answer"].lower()

def test_irrelevant_query(consultant_agent):
    """Тест: вопрос о борще не должен находить релевантной информации в базе"""
    result = consultant_agent.ask_question("Как приготовить борщ?")
    assert result["answer"] != ""  # Ответ может быть сгенерирован, но...
    assert result["sources_count"] == 0  # ...источников в базе нет
    # Дополнительно можно проверить, что в ответе есть фраза о том, что информация не найдена
    assert "нет информации" in result["answer"].lower() or "комендант" in result["answer"].lower()
