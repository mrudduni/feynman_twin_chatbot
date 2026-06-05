"""Persistent chat history manager for Feynman Twin"""
import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from config import CONVERSATION_HISTORY_DIR, PRIMARY_MODEL, GEMINI_API_KEY

logger = logging.getLogger(__name__)

class ChatHistoryManager:
    """Manages persistent conversation storage on disk."""
    
    def __init__(self, history_dir: Path = CONVERSATION_HISTORY_DIR):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_file_path(self, conv_id: str) -> Path:
        return self.history_dir / f"{conv_id}.json"
        
    def create_conversation(self) -> dict:
        """Create a new conversation with a UUID, title, and timestamp."""
        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        conv = {
            "id": conv_id,
            "title": "New Conversation",
            "created_at": now,
            "last_updated": now,
            "messages": [],
            "metadata": {}
        }
        self._save_conversation(conv_id, conv)
        return conv
        
    def add_message(self, conv_id: str, role: str, content: str, metadata: Optional[dict] = None) -> dict:
        """Add a message to a conversation."""
        conv = self.get_conversation(conv_id)
        if not conv:
            # If it doesn't exist, create it with this ID
            now = datetime.now().isoformat()
            conv = {
                "id": conv_id,
                "title": "New Conversation",
                "created_at": now,
                "last_updated": now,
                "messages": [],
                "metadata": {}
            }
            
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        conv["messages"].append(message)
        conv["last_updated"] = datetime.now().isoformat()
        self._save_conversation(conv_id, conv)
        return message
        
    def list_conversations(self, limit: int = 50) -> List[dict]:
        """List conversations sorted by last_updated descending."""
        conversations = []
        for file in self.history_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    conv = json.load(f)
                    conversations.append({
                        "id": conv.get("id"),
                        "title": conv.get("title", "New Conversation"),
                        "last_updated": conv.get("last_updated"),
                        "message_count": len(conv.get("messages", []))
                    })
            except Exception as e:
                logger.error(f"Error reading conversation file {file}: {e}")
                
        # Sort by last_updated descending
        conversations.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
        return conversations[:limit]
        
    def get_conversation(self, conv_id: str) -> Optional[dict]:
        """Get full conversation with all messages."""
        file_path = self._get_file_path(conv_id)
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading conversation {conv_id}: {e}")
            return None
            
    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation file from disk."""
        file_path = self._get_file_path(conv_id)
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                logger.error(f"Error deleting conversation {conv_id}: {e}")
                return False
        return False
        
    def rename_conversation(self, conv_id: str, title: str) -> Optional[dict]:
        """Rename a conversation."""
        conv = self.get_conversation(conv_id)
        if not conv:
            return None
        conv["title"] = title
        conv["last_updated"] = datetime.now().isoformat()
        self._save_conversation(conv_id, conv)
        return conv
        
    def auto_title(self, conv_id: str, first_message: str) -> str:
        """Generate a title using Gemini model."""
        prompt = f"""Generate a brief, engaging 3 to 5 word title for a conversation that starts with the user asking:
"{first_message}"

Do not include any quotes, markdown formatting, or prefix. Provide only the title itself."""
        try:
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not set")
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(prompt)
            title = res.content.strip().strip('"').strip("'").replace("**", "").replace("*", "")
            if not title:
                title = first_message[:30] + "..." if len(first_message) > 30 else first_message
            return title
        except Exception as e:
            logger.warning(f"Error auto-titling conversation: {e}")
            # Fallback to first few words
            words = first_message.split()
            if len(words) > 4:
                return " ".join(words[:4]) + "..."
            return first_message
            
    def get_recent_messages(self, conv_id: str, limit: int = 10) -> List[dict]:
        """Get recent messages for a conversation."""
        conv = self.get_conversation(conv_id)
        if not conv:
            return []
        messages = conv.get("messages", [])
        return messages[-limit:]
            
    def _save_conversation(self, conv_id: str, conv: dict):
        file_path = self._get_file_path(conv_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(conv, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving conversation {conv_id}: {e}")
