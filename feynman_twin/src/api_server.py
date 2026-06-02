"""HTTP API server for the Feynman Digital Twin."""
from pathlib import Path
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    if twin is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    answer, metadata = twin.answer_question(question)
    return ChatResponse(answer=answer, metadata=metadata)

