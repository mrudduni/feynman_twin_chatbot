"""HTTP API server for the Feynman Digital Twin."""
from pathlib import Path
import sys
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Ensure sibling modules (main.py/config.py/etc.) resolve regardless of
# whether uvicorn is launched from project root or from src/.
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from main import FeynmanTwin


env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


app = FastAPI(title="Feynman Twin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    answer_length: str = Field(default="medium", pattern="^(brief|medium|detailed)$")
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    metadata: dict
    conversation_id: str


twin: FeynmanTwin | None = None


@app.on_event("startup")
def startup_event() -> None:
    """Initialize the twin once when server starts."""
    global twin
    twin = FeynmanTwin()


@app.get("/api/health")
def health() -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return {"status": "ok", "rag_ready": twin.rag_ready}


@app.get("/api/memory")
def get_memory() -> dict:
    """Get current memory state for visualization"""
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Get session memory - use conversation_history directly
        session_data = twin.memory_manager.session_memory.conversation_history[-10:] if twin.memory_manager.session_memory.conversation_history else []
        
        # Format session data for frontend
        formatted_session = []
        for msg in session_data:
            if msg.get("role") == "user":
                # Store the question
                question = msg.get("content", "")
                formatted_session.append({"question": question, "answer": ""})
            elif msg.get("role") == "assistant" and formatted_session:
                # Add the answer to the last question
                formatted_session[-1]["answer"] = msg.get("content", "")[:200]
        
        # Get persistent memory attributes
        persistent_data = {
            "user_preferences": getattr(twin.memory_manager.persistent_memory, 'user_preferences', {}),
            "insights": getattr(twin.memory_manager.persistent_memory, 'insights', [])[-10:],
            "topic_interests": getattr(twin.memory_manager.persistent_memory, 'topic_interests', {}),
        }
        
        # Get memory stats
        stats = {
            "total_interactions": len(twin.memory_manager.session_memory.conversation_history) // 2,  # Q&A pairs
            "total_insights": len(getattr(twin.memory_manager.persistent_memory, 'insights', [])),
            "topics_discussed": len(twin.memory_manager.session_memory.topics_discussed),
        }
        
        return {
            "session_memory": formatted_session,
            "persistent_memory": persistent_data,
            "stats": stats,
        }
    except Exception as e:
        logger.error(f"Memory retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    conv_id = payload.conversation_id
    if not conv_id:
        # Create a new conversation
        conv = twin.memory_manager.chat_history.create_conversation()
        conv_id = conv["id"]
        # Auto-title based on first question
        title = twin.memory_manager.chat_history.auto_title(conv_id, question)
        twin.memory_manager.chat_history.rename_conversation(conv_id, title)

    answer, metadata = twin.answer_question(question, answer_length=payload.answer_length, conversation_id=conv_id)
    return ChatResponse(answer=answer, metadata=metadata, conversation_id=conv_id)


# ==================== CHAT HISTORY ENDPOINTS ====================

@app.get("/api/conversations")
def get_conversations() -> list:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return twin.memory_manager.chat_history.list_conversations()


@app.post("/api/conversations")
def create_conversation() -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return twin.memory_manager.chat_history.create_conversation()


@app.get("/api/conversations/{id}")
def get_conversation(id: str) -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    conv = twin.memory_manager.chat_history.get_conversation(id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@app.delete("/api/conversations/{id}")
def delete_conversation(id: str) -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    success = twin.memory_manager.chat_history.delete_conversation(id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "success", "message": "Conversation deleted"}


class RenameRequest(BaseModel):
    title: str

@app.patch("/api/conversations/{id}")
def rename_conversation(id: str, payload: RenameRequest) -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    conv = twin.memory_manager.chat_history.rename_conversation(id, payload.title)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


# ==================== TEACH ME MODE ENDPOINTS ====================

@app.post("/api/teach-me/start")
def start_quiz(num_questions: int = 5) -> list:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    from teach_me import TeachMeSession
    twin.teach_me_session = TeachMeSession(twin.memory_manager.teach_me)
    return twin.teach_me_session.start_session(num_questions=num_questions)


class AnswerRequest(BaseModel):
    card_id: str
    user_answer: str

@app.post("/api/teach-me/answer")
def submit_answer(payload: AnswerRequest) -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    if not hasattr(twin, "teach_me_session") or twin.teach_me_session is None:
        from teach_me import TeachMeSession
        twin.teach_me_session = TeachMeSession(twin.memory_manager.teach_me)
        
    try:
        return twin.teach_me_session.submit_answer(payload.card_id, payload.user_answer)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/teach-me/stats")
def get_quiz_stats() -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return twin.memory_manager.get_learning_stats()


@app.get("/api/teach-me/cards")
def get_cards() -> list:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return twin.memory_manager.teach_me.data["cards"]


@app.delete("/api/teach-me/cards/{id}")
def delete_card(id: str) -> dict:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    success = twin.memory_manager.teach_me.remove_card(id)
    if not success:
        raise HTTPException(status_code=404, detail="Card not found")
    return {"status": "success", "message": "Card deleted"}

