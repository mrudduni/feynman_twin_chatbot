"""Memory system for Feynman Twin - session and persistent memory"""
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config import SESSION_MEMORY_FILE, PERSISTENT_MEMORY_FILE, CONVERSATION_HISTORY_DIR, PRIMARY_MODEL, GEMINI_API_KEY
from chat_history import ChatHistoryManager
from teach_me import SpacedRepetitionEngine
from personality import PersonalityAnalyzer
from langchain_google_genai import ChatGoogleGenerativeAI


class SessionMemory:
    """In-session conversation memory"""

    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.session_id = str(uuid.uuid4())[:8]
        self.session_start = datetime.now().isoformat()
        self.topics_discussed: List[str] = []
        self.context_state: Dict[str, Any] = {}

    def add_message(self, role: str, content: str):
        """Add a message to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
        })

    def add_context(self, key: str, value: Any):
        """Store contextual information"""
        self.context_state[key] = value

    def get_context(self, key: str) -> Any:
        """Retrieve contextual information"""
        return self.context_state.get(key)

    def add_topic(self, topic: str):
        """Track discussed topics"""
        if topic not in self.topics_discussed:
            self.topics_discussed.append(topic)

    def get_conversation_summary(self) -> str:
        """Get summary of conversation for context"""
        if not self.conversation_history:
            return ""

        summary = f"Session {self.session_id}\n"
        summary += f"Topics discussed: {', '.join(self.topics_discussed)}\n"
        summary += "Recent exchanges:\n"

        # Include last 5 exchanges
        for msg in self.conversation_history[-10:]:
            role = msg["role"].upper()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary += f"  {role}: {content}\n"

        return summary

    def save_session(self) -> Path:
        """Save session to file for later reference"""
        session_file = CONVERSATION_HISTORY_DIR / f"session_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "session_id": self.session_id,
            "session_start": self.session_start,
            "session_end": datetime.now().isoformat(),
            "topics_discussed": self.topics_discussed,
            "conversation_history": self.conversation_history,
            "context_state": self.context_state,
        }

        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Session saved to {session_file}")
            return session_file
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return None


class PersistentMemory:
    """Long-term memory across sessions"""

    def __init__(self):
        self.memory_file = PERSISTENT_MEMORY_FILE
        self.data = self._load_memory()

    def _load_memory(self) -> Dict:
        """Load persistent memory from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading persistent memory: {e}")
                return self._initialize_memory()
        else:
            return self._initialize_memory()

    def _initialize_memory(self) -> Dict:
        """Initialize new persistent memory structure"""
        return {
            "created_at": datetime.now().isoformat(),
            "user_profile": {},
            "learned_facts": [],
            "frequently_discussed_topics": [],
            "user_preferences": {},
            "interaction_count": 0,
            "key_insights": [],
        }

    def update_user_profile(self, key: str, value: Any):
        """Update user profile information"""
        if "user_profile" not in self.data:
            self.data["user_profile"] = {}
        self.data["user_profile"][key] = value
        self._save_memory()

    def get_user_profile(self) -> Dict:
        """Retrieve user profile"""
        return self.data.get("user_profile", {})

    def add_learned_fact(self, fact: str):
        """Store a learned fact or insight"""
        fact_entry = {
            "fact": fact,
            "learned_at": datetime.now().isoformat(),
            "relevance": 1.0,
        }
        if "learned_facts" not in self.data:
            self.data["learned_facts"] = []
        self.data["learned_facts"].append(fact_entry)
        self._save_memory()

    def get_learned_facts(self, limit: int = 10) -> List[str]:
        """Get most relevant learned facts"""
        facts = self.data.get("learned_facts", [])
        # Sort by relevance and recency
        sorted_facts = sorted(
            facts,
            key=lambda x: (x.get("relevance", 0), x.get("learned_at", "")),
            reverse=True,
        )
        return [f["fact"] for f in sorted_facts[:limit]]

    def track_topic(self, topic: str):
        """Track frequently discussed topics"""
        topics = self.data.get("frequently_discussed_topics", [])
        for t in topics:
            if t["topic"] == topic:
                t["count"] += 1
                t["last_discussed"] = datetime.now().isoformat()
                self._save_memory()
                return

        # New topic
        topics.append({
            "topic": topic,
            "count": 1,
            "first_discussed": datetime.now().isoformat(),
            "last_discussed": datetime.now().isoformat(),
        })
        self.data["frequently_discussed_topics"] = topics
        self._save_memory()

    def increment_interaction_count(self):
        """Track number of interactions"""
        self.data["interaction_count"] = self.data.get("interaction_count", 0) + 1
        self._save_memory()

    def add_insight(self, insight: str):
        """Store key insights from interactions"""
        insight_entry = {
            "insight": insight,
            "timestamp": datetime.now().isoformat(),
        }
        if "key_insights" not in self.data:
            self.data["key_insights"] = []
        self.data["key_insights"].append(insight_entry)
        self._save_memory()

    def get_insights(self, limit: int = 5) -> List[str]:
        """Retrieve key insights"""
        insights = self.data.get("key_insights", [])
        return [i["insight"] for i in insights[-limit:]]

    def set_preference(self, key: str, value: Any):
        """Store user preferences"""
        if "user_preferences" not in self.data:
            self.data["user_preferences"] = {}
        self.data["user_preferences"][key] = value
        self._save_memory()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve user preference"""
        prefs = self.data.get("user_preferences", {})
        return prefs.get(key, default)

    def _save_memory(self):
        """Save memory to persistent storage"""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving persistent memory: {e}")

    def get_memory_summary(self) -> str:
        """Get summary of persistent memory"""
        summary = "Memory Summary:\n"
        summary += f"Total interactions: {self.data.get('interaction_count', 0)}\n"

        topics = self.data.get("frequently_discussed_topics", [])
        if topics:
            summary += f"Top topics: {', '.join([t['topic'] for t in topics[:3]])}\n"

        insights = self.get_insights(3)
        if insights:
            summary += "Recent insights:\n"
            for i in insights:
                summary += f"  - {i}\n"

        return summary


class MemoryManager:
    """Unified memory management"""

    def __init__(self):
        self.session_memory = SessionMemory()
        self.persistent_memory = PersistentMemory()
        self.chat_history = ChatHistoryManager()
        self.teach_me = SpacedRepetitionEngine()

    def get_context_for_query(self) -> str:
        """Get combined context from both memory systems"""
        context = ""

        # Add persistent memory context
        context += "Your long-term knowledge:\n"
        context += self.persistent_memory.get_memory_summary()
        context += "\n"

        # Add session context
        conversation = self.session_memory.get_conversation_summary()
        if conversation:
            context += "Current session context:\n"
            context += conversation

        return context

    def get_recent_messages(self, conv_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve recent messages for a conversation"""
        return self.chat_history.get_recent_messages(conv_id, limit=limit)

    def record_interaction(self, user_message: str, assistant_response: str, conv_id: str = None):
        """Record an interaction in both memory systems, persistent chat file, and teach me mode."""
        # Session memory
        self.session_memory.add_message("user", user_message)
        self.session_memory.add_message("assistant", assistant_response)

        # Persistent memory
        self.persistent_memory.increment_interaction_count()

        # Save to chat history file if conv_id provided
        if conv_id:
            # We can compute/pass some metadata
            self.chat_history.add_message(conv_id, "user", user_message)
            self.chat_history.add_message(conv_id, "assistant", assistant_response)

        # Extract topics (simple keyword extraction)
        keywords = ["physics", "quantum", "learning", "science", "experiment", "understanding"]
        for keyword in keywords:
            if keyword.lower() in user_message.lower():
                self.session_memory.add_topic(keyword)
                self.persistent_memory.track_topic(keyword)

        # Trigger card auto-generation for qualifying discussions
        if len(assistant_response) > 300:
            score = PersonalityAnalyzer.score_feynman_alignment(assistant_response)
            if score > 0.6:
                self.auto_generate_card(user_message, assistant_response, conv_id)

    def auto_generate_card(self, user_message: str, assistant_response: str, conv_id: str = None):
        """Auto-generate a quiz card using LLM based on conversation context."""
        prompt = f"""Based on the following explanation by Richard Feynman:
        
"{assistant_response}"

Create a quiz question that tests the user's understanding of the main physical concept explained. The question should follow the Feynman Technique style (asking the user to explain it in their own words or using an analogy).

Return a JSON object with exactly these fields:
- "topic": The general topic (e.g. "quantum mechanics", "entropy", "forces")
- "question": The Feynman-style review question
- "expected_key_points": A list of 2-4 key conceptual points that the user's explanation should include.

Do not include any markdown format tags like ```json. Output only valid raw JSON."""
        try:
            if not GEMINI_API_KEY:
                return
            llm = ChatGoogleGenerativeAI(model=PRIMARY_MODEL, google_api_key=GEMINI_API_KEY)
            res = llm.invoke(prompt)
            clean_res = res.content.strip().replace("```json", "").replace("```", "")
            if clean_res.startswith("json"):
                clean_res = clean_res[4:].strip()
            data = json.loads(clean_res)
            
            topic = data.get("topic", "physics")
            question = data.get("question")
            expected_key_points = data.get("expected_key_points", [])
            
            if question and expected_key_points:
                self.teach_me.add_card(
                    topic=topic,
                    question=question,
                    expected_key_points=expected_key_points,
                    created_from=conv_id
                )
                logger.info(f"Auto-generated Teach Me card for topic: {topic}")
        except Exception as e:
            logger.error(f"Error auto-generating card: {e}")

    def get_learning_stats(self) -> dict:
        """Fetch statistics for Teach Me Mode."""
        return self.teach_me.get_stats()

    def save_session(self) -> Path:
        """Save current session"""
        return self.session_memory.save_session()

    def load_previous_session(self, session_file: Path) -> bool:
        """Load a previous session"""
        try:
            with open(session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            self.session_memory.conversation_history = session_data.get("conversation_history", [])
            self.session_memory.topics_discussed = session_data.get("topics_discussed", [])
            logger.info(f"Loaded session from {session_file}")
            return True
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
