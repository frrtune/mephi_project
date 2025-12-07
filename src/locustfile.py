# locustfile.py

from locust import HttpUser, task, between
import random
import os

# Списки вопросов для консультанта и психолога
consultant_questions = [
    "Какие адреса общежитий МИФИ?",
    "Сколько стоит проживание?",
    "Какие документы нужны для заселения?",
    "Есть ли интернет в общежитиях?",
    "Во сколько комендантский час?"
]

emotional_questions = [
    "Мне плохо",
    "Я чувствую себя одиноко",
    "У меня стресс",
    "Не могу справиться",
    "Помогите"
]

class BotUser(HttpUser):
    """Класс пользователя для нагрузочного тестирования бота."""

    # Ожидание между задачами (в секундах)
    wait_time = between(1, 5)

    # Получаем токен бота из переменной окружения
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не установлен в переменных окружения!")

    # Захардкодим chat_id для тестирования. В реальности нужно использовать разные ID.
    CHAT_ID = os.getenv("TEST_CHAT_ID", "123456789")  # Замените на реальный ID

    @task(3)  # Приоритет 3: выполняется в 3 раза чаще, чем ask_psychologist
    def ask_consultant(self):
        """Отправляет случайный вопрос консультанту."""
        question = random.choice(consultant_questions)
        url = f"/bot{self.BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': self.CHAT_ID,
            'text': question
        }
        with self.client.post(url, data=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}: {response.text}")

    @task(1)  # Приоритет 1
    def ask_psychologist(self):
        """Отправляет случайный вопрос психологу."""
        question = random.choice(emotional_questions)
        url = f"/bot{self.BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': self.CHAT_ID,
            'text': question
        }
        with self.client.post(url, data=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}: {response.text}")
