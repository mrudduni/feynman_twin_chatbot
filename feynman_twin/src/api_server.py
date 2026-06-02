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


class ChatResponse(BaseModel):
    answer: str
    metadata: dict


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

    answer, metadata = twin.answer_question(question, answer_length=payload.answer_length)
    return ChatResponse(answer=answer, metadata=metadata)

