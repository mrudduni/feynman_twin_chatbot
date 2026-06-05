"""Feynman Digital Twin Package"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "Digital Twin of Richard Feynman - Physics educator and Nobel laureate"

from .main import FeynmanTwin
from .memory_system import MemoryManager
from .personality import FeynmanPersonality
from .rag_system import RAGSystem
from .chat_history import ChatHistoryManager
from .teach_me import SpacedRepetitionEngine

__all__ = [
    "FeynmanTwin",
    "MemoryManager",
    "FeynmanPersonality",
    "RAGSystem",
    "ChatHistoryManager",
    "SpacedRepetitionEngine",
]
