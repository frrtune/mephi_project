import logging
import sqlite3
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

from llm.client import llm_client
from llm.prompts.consultant_prompts import get_consultant_prompt

logger = logging.getLogger(__name__)

class RAGConsultantAgent:
    """
    Агент-Консультант с поиском через вашу SQLite векторную базу с VSS
    """
    
    def __init__(self, db_path: str = 'mipti_dormitory_db.db'):
        self.name = "Консультант с RAG"
        self.db_path = db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.conversation_history: List[Dict] = []
        
        logger.info(f"RAGConsultantAgent инициализирован с базой: {db_path}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получение соединения с базой данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Включаем расширения VSS
            conn.enable_load_extension(True)
            try:
                conn.load_extension("vector")
                conn.load_extension("vss0")
            except Exception as e:
                logger.warning(f"Не удалось загрузить расширения VSS: {e}")
            
            return conn
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
    
    async def ask_question(self, question: str, user_id: str = None, limit: int = 5) -> Dict[str, Any]:
        """
        Основной метод для вопросов с RAG через вашу базу данных
        
        Args:
            question: Вопрос пользователя
            user_id: ID пользователя для истории
            limit: Количество релевантных фрагментов для поиска
            
        Returns:
            Dict с ответом и метаданными
        """
        try:
            # 1. Поиск релевантных документов в векторной базе
            relevant_docs = await self._search_in_database(question, limit=limit)
            
            # 2. Формирование контекста из найденных документов
            context = self._format_context(relevant_docs)
            
            # 3. Генерация ответа с использованием контекста
            answer = await self._generate_rag_response(question, context)
            
            # 4. Сохранение в историю
            if user_id:
                self._save_to_history(user_id, question, answer, relevant_docs)
            
            # 5. Формирование результата
            return {
                "answer": answer,
                "sources": relevant_docs,
                "context_used": bool(relevant_docs),
                "sources_count": len(relevant_docs),
                "has_context": context != "В базе знаний нет информации по данному вопросу."
            }
            
        except Exception as e:
            logger.error(f"Ошибка в RAG агенте: {e}")
            return {
                "answer": "Извините, произошла ошибка при обработке вашего вопроса. Попробуйте позже.",
                "sources": [],
                "context_used": False,
                "error": str(e)
            }
    
    async def _search_in_database(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Поиск в векторной базе через VSS
        
        Args:
            query: Поисковый запрос
            limit: Количество результатов
            
        Returns:
            List релевантных документов
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Создаем вектор для поиска
            search_vector = self.model.encode([query])[0].tolist()
            
            # Ищем похожие записи через VSS
            cursor.execute('''
                SELECT 
                    t.id, 
                    t.text, 
                    t.category,
                    t.tags,
                    vss_distance AS similarity
                FROM dormitory_vectors 
                JOIN dormitory_info t ON t.id = dormitory_vectors.rowid
                WHERE vss_search(vector, ?)
                LIMIT ?
            ''', (search_vector, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            # Форматируем результаты
            formatted_results = []
            for row in results:
                doc_id, text, category, tags, similarity = row
                
                # Конвертируем расстояние в схожесть (чем меньше расстояние - тем больше схожесть)
                similarity_score = 1.0 / (1.0 + similarity) if similarity > 0 else 1.0
                
                formatted_results.append({
                    'id': doc_id,
                    'content': text,
                    'source': 'База знаний общежития МИФИ',
                    'category': category,
                    'tags': tags,
                    'similarity': similarity_score,
                    'distance': similarity
                })
            
            logger.info(f"Найдено {len(formatted_results)} документов для запроса: '{query}'")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Ошибка поиска в векторной базе: {e}")
            return []
    
    def _format_context(self, documents: List[Dict]) -> str:
        """Форматирование найденных документов в контекст"""
        if not documents:
            return "В базе знаний нет информации по данному вопросу."
        
        context_parts = ["📚 Релевантная информация из базы знаний общежития МИФИ:"]
        
        for i, doc in enumerate(documents, 1):
            category = doc.get('category', 'Общая информация')
            content = doc.get('content', '')
            similarity = doc.get('similarity', 0)
            
            context_parts.append(
                f"\n--- Запись {i}: {category} (релевантность: {similarity:.2f}) ---\n"
                f"{content}"
            )
        
        return "\n".join(context_parts)
    
    async def _generate_rag_response(self, question: str, context: str) -> str:
        """Генерация ответа с использованием RAG контекста"""
        prompt = get_consultant_prompt(context, question)
        
        try:
            response = await llm_client.generate_response(
                prompt, 
                temperature=0.3,  # Более детерминированные ответы
                max_tokens=600
            )
            return response.strip()
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            # Fallback ответ на основе контекста
            if context and "нет информации" not in context:
                return (
                    "На основе информации из базы знаний общежития МИФИ:\n\n"
                    f"{context}\n\n"
                    "Для уточнения деталей обратитесь к коменданту вашего общежития."
                )
            else:
                return "К сожалению, в базе знаний общежития МИФИ нет информации по этому вопросу. Рекомендую обратиться к коменданту лично или в студенческий офис."
    
    def _save_to_history(self, user_id: str, question: str, answer: str, sources: List[Dict]):
        """Сохранение диалога в историю"""
        conversation = {
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "sources": [f"{s.get('category', '')}: {s.get('content', '')[:50]}..." for s in sources],
            "sources_count": len(sources),
            "timestamp": self._get_current_timestamp()
        }
        self.conversation_history.append(conversation)
        
        # Ограничиваем историю последними 100 диалогами
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def get_conversation_history(self, user_id: str = None) -> List[Dict]:
        """Получение истории диалогов"""
        if user_id:
            return [conv for conv in self.conversation_history if conv['user_id'] == user_id]
        return self.conversation_history
    
    def _get_current_timestamp(self) -> str:
        """Текущее время для истории"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def add_knowledge(self, text: str, category: str = "Общая информация", tags: str = "общежитие, МИФИ") -> int:
        """
        Добавление новой информации в базу знаний
        
        Args:
            text: Текст для добавления
            category: Категория информации
            tags: Теги для поиска
            
        Returns:
            ID добавленной записи
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Создаем векторное представление
            vector = self.model.encode([text])[0].tolist()
            
            # Сохраняем текст
            cursor.execute(
                'INSERT INTO dormitory_info (text, category, tags) VALUES (?, ?, ?)',
                (text, category, tags)
            )
            text_id = cursor.lastrowid
            
            # Сохраняем вектор
            conn.execute(
                'INSERT INTO dormitory_vectors(rowid, vector) VALUES (?, ?)',
                (text_id, vector)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Добавлена новая запись в базу знаний (ID: {text_id})")
            return text_id
            
        except Exception as e:
            logger.error(f"Ошибка добавления в базу знаний: {e}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Получение статистики базы данных"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Количество записей
            cursor.execute('SELECT COUNT(*) FROM dormitory_info')
            total_records = cursor.fetchone()[0]
            
            # Распределение по категориям
            cursor.execute('SELECT category, COUNT(*) FROM dormitory_info GROUP BY category')
            categories = cursor.fetchall()
            
            conn.close()
            
            return {
                "total_records": total_records,
                "categories": dict(categories),
                "database_path": self.db_path
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"error": str(e)}
