"""Configuration for Feynman Digital Twin"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_MARKDOWN = PROJECT_ROOT / "data" / "markdown"
EMBEDDINGS_DB = PROJECT_ROOT / "embeddings"
MEMORY_DIR = PROJECT_ROOT / "memory"

# Create directories if they don't exist
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
DATA_MARKDOWN.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DB.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gemini-2.5-flash")
# Keep fallback valid by default for current Gemini API availability.
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-2.5-flash")

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_MODEL_FALLBACK = ["models/gemini-embedding-2"]  # Fallback models to try
CHROMA_DB_NAME = "feynman_knowledge"

# Data collection
FEYNMAN_SOURCES = {
    "arxiv_query": "Richard Feynman physics",
    "wikipedia_pages": ["Richard Feynman", "Quantum electrodynamics", "Feynman diagram"],
    "quotes_file": "feynman_quotes.txt",  # Will be created
}

# Memory configuration
SESSION_MEMORY_FILE = MEMORY_DIR / "session_memory.json"
PERSISTENT_MEMORY_FILE = MEMORY_DIR / "persistent_memory.json"
CONVERSATION_HISTORY_DIR = MEMORY_DIR / "conversations"
CONVERSATION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
TEACH_ME_CARDS_FILE = MEMORY_DIR / "teach_me_cards.json"

# Personality parameters
FEYNMAN_PERSONALITY = {
    "curiosity": 0.95,
    "humor": 0.85,
    "clarity": 0.90,
    "critical_thinking": 0.95,
    "teaching_style": "socratic",  # Feynman's famous teaching method
}
