"""
Пакет для работы с векторной базой данных общежитий МИФИ
"""

from .base import (
    create_database,
    add_preloaded_data,
    add_manual_data,
    search_data,
    view_all_data,
    model
)

__all__ = [
    'create_database',
    'add_preloaded_data', 
    'add_manual_data',
    'search_data',
    'view_all_data',
    'model'
]

__version__ = '1.0.0'
