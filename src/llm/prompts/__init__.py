"""
Инициализация модуля промптов для LLM агентов
"""

from .consultant_prompts import get_consultant_rag_prompt
from .psychologist_prompts import (
    get_psychologist_system_prompt,
    get_psychologist_prompt_with_history,
    get_crisis_intervention_prompt,
    get_stress_management_prompt,
    get_academic_support_prompt,
    get_welcome_message,
    get_privacy_notice,
    detect_crisis_keywords,
    format_history
)

__all__ = [
    # Консультант (RAG для общежитий)
    "get_consultant_rag_prompt",
    
    # Психолог (эмоциональная поддержка)
    "get_psychologist_system_prompt",
    "get_psychologist_prompt_with_history",
    "get_crisis_intervention_prompt",
    "get_stress_management_prompt",
    "get_academic_support_prompt",
    "get_welcome_message",
    "get_privacy_notice",
    "detect_crisis_keywords",
    "format_history",
]
