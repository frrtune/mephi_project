"""
Модели данных для базы знаний МИФИ
Просто и понятно для студенческого проекта
"""

class KnowledgeItem:
    """Простая модель для хранения информации о МИФИ"""
    
    def __init__(self, text: str, category: str, tags: str = ""):
        """
        Инициализация элемента знаний
        
        Args:
            text: Текст информации
            category: Категория (Адреса, Правила, Стоимость, Удобства)
            tags: Ключевые слова для поиска
        """
        self.text = text
        self.category = category
        self.tags = tags.split(',') if tags else []
    
    def __str__(self) -> str:
        """Строковое представление"""
        return f"[{self.category}] {self.text}"
    
    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            'text': self.text,
            'category': self.category,
            'tags': self.tags
        }
    
    def matches_query(self, query: str) -> bool:
        """
        Проверяет, соответствует ли элемент поисковому запросу
        
        Args:
            query: Поисковый запрос
            
        Returns:
            bool: True если есть совпадение
        """
        query_lower = query.lower()
        
        # Проверяем текст
        if query_lower in self.text.lower():
            return True
        
        # Проверяем категорию
        if query_lower in self.category.lower():
            return True
        
        # Проверяем теги
        for tag in self.tags:
            if query_lower in tag.lower():
                return True
        
        return False


class Session:
    """Модель сессии диалога с психологом"""
    
    def __init__(self, session_id: str, user_id: int, start_time: str, message_count: int = 0):
        """
        Инициализация сессии
        
        Args:
            session_id: Уникальный ID сессии
            user_id: ID пользователя в Telegram
            start_time: Время начала сессии
            message_count: Количество сообщений в сессии
        """
        self.session_id = session_id
        self.user_id = user_id
        self.start_time = start_time
        self.message_count = message_count
        self.messages = []  # Список объектов Message
    
    def add_message(self, message):
        """Добавление сообщения в сессию"""
        self.messages.append(message)
        self.message_count += 1
    
    def get_recent_messages(self, limit: int = 10):
        """Получение последних сообщений"""
        return self.messages[-limit:] if self.messages else []
    
    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'start_time': self.start_time,
            'message_count': self.message_count,
            'has_messages': len(self.messages) > 0
        }


class Message:
    """Модель сообщения в сессии"""
    
    def __init__(self, role: str, content: str, timestamp: str):
        """
        Инициализация сообщения
        
        Args:
            role: 'user' или 'assistant'
            content: Текст сообщения
            timestamp: Время отправки
        """
        self.role = role  # 'user' или 'assistant'
        self.content = content
        self.timestamp = timestamp
    
    def __str__(self) -> str:
        """Строковое представление"""
        return f"{self.role}: {self.content[:50]}..."
    
    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp,
            'is_user': self.role == 'user',
            'is_assistant': self.role == 'assistant'
        }


class UserStats:
    """Модель статистики пользователя"""
    
    def __init__(self, user_id: int, total_sessions: int = 0, total_messages: int = 0):
        """
        Инициализация статистики
        
        Args:
            user_id: ID пользователя
            total_sessions: Всего сессий
            total_messages: Всего сообщений
        """
        self.user_id = user_id
        self.total_sessions = total_sessions
        self.total_messages = total_messages
        self.last_activity = None
    
    def update_activity(self):
        """Обновление времени последней активности"""
        from datetime import datetime
        self.last_activity = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            'user_id': self.user_id,
            'total_sessions': self.total_sessions,
            'total_messages': self.total_messages,
            'last_activity': self.last_activity
        }


# ==============================================
# ПРЕДОПРЕДЕЛЕННЫЕ ДАННЫЕ МИФИ
# ==============================================

class MIFIKnowledgeBase:
    """Класс с предопределенными данными о МИФИ"""
    
    @staticmethod
    def get_all_knowledge() -> list[KnowledgeItem]:
        """Возвращает все знания о МИФИ"""
        return [
            # АДРЕСА ОБЩЕЖИТИЙ
            KnowledgeItem("Общежитие №1 МИФИ: Москва, улица Москворечье, 2к1", "Адреса", "общежитие1, адрес, местоположение"),
            KnowledgeItem("Общежитие №2 МИФИ: Москва, улица Москворечье, 2к2", "Адреса", "общежитие2, адрес, местоположение"),
            KnowledgeItem("Общежитие №3 МИФИ: Москва, улица Москворечье, 19к3", "Адреса", "общежитие3, адрес, местоположение"),
            KnowledgeItem("Общежитие №4 МИФИ: Москва, улица Москворечье, 19к4", "Адреса", "общежитие4, адрес, местоположение"),
            KnowledgeItem("Общежитие №5 МИФИ: Москва, улица Кошкина, 11", "Адреса", "общежитие5, адрес, местоположение"),
            KnowledgeItem("Общежитие №7 МИФИ: Москва, улица Шкулева, 27", "Адреса", "общежитие7, адрес, местоположение"),
            KnowledgeItem("Общежитие №8 МИФИ: Москва, Пролетарский проспект, 8к2", "Адреса", "общежитие8, адрес, местоположение"),
            KnowledgeItem("Общежитие №9 МИФИ: Москва, Пролетарский проспект, 8к1", "Адреса", "общежитие9, адрес, местоположение"),
            
            # СТОИМОСТЬ ПРОЖИВАНИЯ
            KnowledgeItem("Стоимость проживания в общежитии МИФИ: от 1200 до 2500 рублей в месяц", "Стоимость", "цена, оплата, проживание, деньги"),
            KnowledgeItem("Оплата общежития производится до 10 числа каждого месяца", "Стоимость", "оплата, сроки, дата"),
            
            # ПРАВИЛА ПРОЖИВАНИЯ
            KnowledgeItem("Гости в общежитии разрешены до 23:00", "Правила", "гости, время, посещение"),
            KnowledgeItem("Тишина в общежитии с 23:00 до 7:00", "Правила", "тишина, ночь, отдых"),
            KnowledgeItem("Курить в общежитии запрещено", "Правила", "курение, запрет, здоровье"),
            KnowledgeItem("За нарушение правил проживания могут выселить", "Правила", "нарушение, выселение, дисциплина"),
            
            # УДОБСТВА И ИНФРАСТРУКТУРА
            KnowledgeItem("В каждом общежитии есть кухня на этаже", "Удобства", "кухня, готовка, еда"),
            KnowledgeItem("В общежитиях есть бесплатный Wi-Fi", "Удобства", "интернет, wi-fi, связь"),
            KnowledgeItem("Рядом с общежитиями есть столовая МИФИ", "Удобства", "столовая, питание, еда"),
            KnowledgeItem("В общежитиях есть прачечные комнаты", "Удобства", "прачечная, стирка, белье"),
            KnowledgeItem("Есть комнаты для самостоятельной подготовки", "Удобства", "учеба, подготовка, комната"),
            KnowledgeItem("Общежития в 10 минутах от учебных корпусов", "Удобства", "расстояние, дорога, корпуса"),
            
            # ДОКУМЕНТЫ И ЗАСЕЛЕНИЕ
            KnowledgeItem("Для заселения нужен паспорт", "Документы", "паспорт, документ, удостоверение"),
            KnowledgeItem("Нужна справка о состоянии здоровья", "Документы", "справка, здоровье, медосмотр"),
            KnowledgeItem("Нужны фотографии 3x4", "Документы", "фото, фотография, снимок"),
            KnowledgeItem("Нужно заявление в деканате", "Документы", "заявление, деканат, оформление"),
            
            # ДЛЯ ИНОГОРОДНИХ СТУДЕНТОВ
            KnowledgeItem("Иногородние студенты имеют приоритет при заселении", "Для иногородних", "иногородние, приоритет, заселение"),
            KnowledgeItem("Ближайшее метро к общежитиям - Каширская", "Для иногородних", "метро, транспорт, проезд, Каширская"),
        ]
    
    @staticmethod
    def get_knowledge_by_category(category: str) -> list[KnowledgeItem]:
        """Возвращает знания по категории"""
        return [item for item in MIFIKnowledgeBase.get_all_knowledge() 
                if item.category.lower() == category.lower()]
    
    @staticmethod
    def search_knowledge(query: str) -> list[KnowledgeItem]:
        """Поиск знаний по запросу"""
        query_lower = query.lower()
        results = []
        
        for item in MIFIKnowledgeBase.get_all_knowledge():
            if (query_lower in item.text.lower() or 
                query_lower in item.category.lower() or
                any(query_lower in tag.lower() for tag in item.tags)):
                results.append(item)
        
        return results
    
    @staticmethod
    def get_categories() -> list[str]:
        """Возвращает список всех категорий"""
        categories = set()
        for item in MIFIKnowledgeBase.get_all_knowledge():
            categories.add(item.category)
        return list(categories)


# ==============================================
# УТИЛИТЫ ДЛЯ РАБОТЫ С МОДЕЛЯМИ
# ==============================================

def create_test_session() -> Session:
    """Создание тестовой сессии"""
    import uuid
    session_id = str(uuid.uuid4())
    from datetime import datetime
    
    return Session(
        session_id=session_id,
        user_id=99999,
        start_time=datetime.now().isoformat()
    )

def create_test_message(role: str, content: str) -> Message:
    """Создание тестового сообщения"""
    from datetime import datetime
    
    return Message(
        role=role,
        content=content,
        timestamp=datetime.now().isoformat()
    )

# ==============================================
# ТЕСТИРОВАНИЕ
# ==============================================

if __name__ == "__main__":
    print("🧪 Тестирование моделей данных МИФИ")
    print("=" * 50)
    
    # Тест базы знаний
    all_knowledge = MIFIKnowledgeBase.get_all_knowledge()
    print(f"Всего фактов о МИФИ: {len(all_knowledge)}")
    
    # Тест категорий
    categories = MIFIKnowledgeBase.get_categories()
    print(f"\nКатегории: {', '.join(categories)}")
    
    # Тест поиска
    search_query = "адрес"
    search_results = MIFIKnowledgeBase.search_knowledge(search_query)
    print(f"\nПоиск '{search_query}': найдено {len(search_results)} результатов")
    
    for i, item in enumerate(search_results[:3], 1):
        print(f"  {i}. {item}")
    
    # Тест сессии
    print("\n🧪 Тест модели сессии:")
    session = create_test_session()
    print(f"Создана сессия: {session.session_id}")
    
    # Добавляем сообщения
    user_msg = create_test_message("user", "Привет, как дела?")
    bot_msg = create_test_message("assistant", "Привет! Я хорошо, а у тебя?")
    
    session.add_message(user_msg)
    session.add_message(bot_msg)
    
    print(f"Сообщений в сессии: {session.message_count}")
    print(f"Сессия в dict: {session.to_dict()}")
    
    # Тест статистики
    print("\n🧪 Тест статистики:")
    stats = UserStats(user_id=12345, total_sessions=5, total_messages=42)
    stats.update_activity()
    print(f"Статистика user_id={stats.user_id}: {stats.to_dict()}")
