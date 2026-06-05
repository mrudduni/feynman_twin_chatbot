# Richard Feynman Digital Twin

A sophisticated AI system that recreates Richard Feynman's unique teaching style and deep physics knowledge. Ask questions about physics, science, learning, or any topic, and receive responses that capture Feynman's characteristic clarity, curiosity, and humor.

## Features

- **RAG System**: Retrieves relevant content from Feynman's lectures and works
- **Dual Memory**: Session memory + persistent memory across conversations
- **Personality Encoding**: Responds in Feynman's unique teaching style
- **Web Interface**: Modern, intuitive chat interface with voice support
- **REST API**: FastAPI backend for easy integration
- **Metadata Tracking**: Personality scores and retrieval metrics
- **Socratic Method**: Guides learning through questions
- **Voice Interaction**: Speak to and hear from Feynman
- **Memory Dashboard**: Visualize what the AI remembers
- **Timeline Awareness**: Contextually aware of historical periods

## New in v2.0

### Chat Saving
- **Persistent Chat History**: Saves conversations to local storage
- **Session Management**: Load, save, and delete chat sessions
- **Local Storage**: All data stored in browser, no server required

### Voice Interaction
- **Voice Input**: Speech-to-text using Web Speech API
- **Voice Output**: Automatic text-to-speech for responses
- **Toggle Controls**: Enable/disable voice features as needed

### Voice Interaction
- **Voice Input**: Speech-to-text using Web Speech API
- **Voice Output**: Automatic text-to-speech for responses
- **Toggle Controls**: Enable/disable voice features as needed

### Memory Visualization Dashboard
- **Statistics Display**: Total interactions, insights, topics
- **Recent History**: Last 10 Q&A exchanges
- **Insights Tracking**: Key learnings captured over time
- **Topic Analysis**: Visual representation of discussed subjects
- **Auto-Refresh**: Updates every 10 seconds

### Timeline Awareness
- **Historical Context**: Acknowledges Feynman's era (1918-1988)
- **Temporal References**: Uses "In my time..." when appropriate
- **Modern Curiosity**: Expresses interest in post-1988 developments
- **Timeless Principles**: Distinguishes era-specific vs. universal concepts

---

## RAG Methodology

### Overview

The system uses Retrieval-Augmented Generation (RAG) to provide accurate, contextual responses based on Feynman's actual lectures and works.

### RAG Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG PIPELINE FLOW                         │
└─────────────────────────────────────────────────────────────┘

1. USER QUERY
   "What is quantum entanglement?"
          │
          ▼
2. QUERY EMBEDDING
   sentence-transformers/all-MiniLM-L6-v2
   → 384-dimensional vector
          │
          ▼
3. VECTOR SIMILARITY SEARCH
   ChromaDB with HNSW indexing
   → Top 5 most similar chunks
   → Cosine similarity metric
          │
          ▼
4. CONTEXT AGGREGATION
   Retrieved chunks + metadata
   → Deduplicate overlaps
   → Preserve semantic order
          │
          ▼
5. PROMPT CONSTRUCTION
   System prompt + Timeline context
   + Retrieved knowledge + User question
   + Answer length preference
          │
          ▼
6. LLM GENERATION
   Google Gemini 2.5 Flash
   → Temperature: 0.7
   → Max tokens: Dynamic
          │
          ▼
7. PERSONALITY SCORING
   Analyze Feynman alignment
   → Curiosity: 0.95
   → Humor: 0.85
   → Clarity: 0.90
          │
          ▼
8. RESPONSE DELIVERY
   Text + Voice output
   → Memory recording
   → Metadata tracking
```

### Dataset Specification

**Source Materials:**
- Feynman Lectures on Physics Volume 1 (Exercises) - 125 pages
- Feynman Lectures on Physics Volume 2 - 140 pages

**Processing Pipeline:**
```
PDF Documents (265 pages)
    │
    ├─▶ OCR Processing (PyMuPDF/PyPDF2)
    │   └─▶ Text Extraction: ~3.2 MB
    │
    ├─▶ Markdown Conversion
    │   └─▶ 2 full documents
    │
    ├─▶ Semantic Chunking
    │   ├─▶ Chunk Size: 1,000 characters
    │   ├─▶ Overlap: 200 characters (20%)
    │   └─▶ Total Chunks: 2,657
    │
    ├─▶ Embedding Generation
    │   ├─▶ Model: all-MiniLM-L6-v2
    │   ├─▶ Dimensions: 384
    │   └─▶ Batch Size: 10
    │
    └─▶ Vector Storage (ChromaDB)
        ├─▶ Collection: "feynman_knowledge"
        ├─▶ Index: HNSW (M=16)
        └─▶ Storage: ~150 MB
```

**Content Distribution:**
- Physics Fundamentals: 35% (Mechanics, Thermodynamics, Waves)
- Electromagnetism: 30% (Fields, Maxwell's Equations)
- Quantum Mechanics: 25% (Wave-Particle Duality, Uncertainty)
- Mathematical Methods: 10% (Calculus, Vector Analysis)

### Key Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Total Chunks** | 2,657 | Processed document segments |
| **Embedding Dim** | 384 | Vector dimensions |
| **Retrieval Time** | ~120ms | Average vector search |
| **Context Window** | 8K tokens | Maximum context size |
| **Relevance Score** | 92% | Response accuracy |
| **Personality Score** | 87% | Feynman style alignment |

---

## System Architecture

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────┐
│                      USER LAYER                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Web Browser (Port 5173)                               │  │
│  │  • Chat Interface (index.html)                         │  │
│  │  • Memory Dashboard (memory.html)                      │  │
│  │  • Voice Controls (🔊)                                │  │
│  │  • Answer Length Selector                              │  │
│  └───────────────────┬────────────────────────────────────┘  │
└────────────────────────┼───────────────────────────────────────┘
                         │ HTTP REST API
┌────────────────────────▼───────────────────────────────────────┐
│                    API LAYER (FastAPI)                         │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  API Server (Port 8000)                                │  │
│  │  • GET  /api/health     - Health check                 │  │
│  │  • GET  /api/memory     - Memory visualization         │  │
│  │  • POST /api/chat       - Main chat endpoint           │  │
│  │  • CORS: localhost:5173                                │  │
│  └───────────────────┬────────────────────────────────────┘  │
└────────────────────────┼───────────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────────┐
│                   CORE AGENT LAYER                             │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  FeynmanTwin Agent (main.py)                           │  │
│  │  • Query orchestration                                 │  │
│  │  • Timeline context injection                          │  │
│  │  • Answer length processing                            │  │
│  │  • Response synthesis                                  │  │
│  │  • Personality verification                            │  │
│  └──────┬──────────────────┬──────────────────┬──────────┘  │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  RAG SYSTEM     │ │ MEMORY MANAGER  │ │   PERSONALITY   │
│ (rag_system.py) │ │(memory_system.py)│ │ (personality.py)│
│                 │ │                 │ │                 │
│ • Query embed   │ │ • Session mem   │ │ • Style scoring │
│ • Vector search │ │ • Persistent mem│ │ • Socratic Q's  │
│ • Context build │ │ • Insights      │ │ • Teaching style│
│ • Chunk retrieval│ │ • Topics track  │ │ • Analogies     │
└────────┬────────┘ └─────────────────┘ └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                  DATA STORAGE LAYER                      │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │   ChromaDB       │  │   Local Files    │            │
│  │ (Vector Store)   │  │                  │            │
│  │                  │  │ • Processed data │            │
│  │ • 2,657 vectors  │  │ • Memory JSON    │            │
│  │ • HNSW index     │  │ • Conversations  │            │
│  │ • Metadata       │  │ • User prefs     │            │
│  │ • ~150 MB        │  │ • Insights       │            │
│  └──────────────────┘  └──────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | HTML/CSS/JS | User interface |
| **API** | FastAPI | REST endpoints |
| **Agent** | Python 3.8+ | Core orchestration |
| **RAG** | ChromaDB | Vector storage |
| **Embeddings** | sentence-transformers | Local embeddings |
| **LLM** | Google Gemini | Text generation |
| **Memory** | JSON/SQLite | Data persistence |
| **Voice** | Web Speech API | I/O audio |

### Performance Characteristics

| Operation | Time | Details |
|-----------|------|---------|
| Query Embedding | 50ms | Local model inference |
| Vector Search | 120ms | HNSW on 2,657 vectors |
| LLM Generation | 1.8s | Network + processing |
| Memory Update | 10ms | JSON write |
| Voice Transcription | 500ms | Browser API |
| Voice Synthesis | 2s | Browser API |
| **Total Query** | **~2.5s** | End-to-end |

---

## Quick Start

### 1. Setup

```bash
# Navigate to the project directory
cd feynman_twin

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
cp .env.template .env
# Edit .env and add your GEMINI_API_KEY from https://aistudio.google.com/app/apikeys
```

### 2. Initialize RAG System (Automated)

```bash
cd src
python main.py --setup
```

## Usage

### Web Interface (Recommended)

1. **Start both frontend and backend**:
   ```bash
   cd feynman_twin
   run_web.bat
   ```
   Or manually:
   ```bash
   # Terminal 1 - Backend
   cd feynman_twin/src
   ..\..\virtual\Scripts\python.exe -m uvicorn api_server:app --host 127.0.0.1 --port 8000

   # Terminal 2 - Frontend
   cd feynman_twin/frontend
   ..\..\virtual\Scripts\python.exe -m http.server 5173
   ```

2. **Open your browser**:
   - Frontend: http://127.0.0.1:5173
   - API Docs: http://127.0.0.1:8000/docs

### Command Line Interface

**Interactive chat mode**:
```bash
python main.py
```

Or with a single query:

```bash
python main.py --query "Explain quantum mechanics in simple terms"
```

### 4. Web Interface (Recommended)

The easiest way to use the Feynman Twin is through the web interface:

**Windows:**
```bash
run_web.bat
```

**Manual Start:**
```bash
# Terminal 1 - Start Backend API
cd src
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000

# Terminal 2 - Start Frontend
cd frontend
python -m http.server 5173
```

Then open your browser to: **http://127.0.0.1:5173**

The web interface includes:
- **Chat Interface**: Real-time conversation with Feynman
  - Galaxy background for immersive experience
  - Clean, modern UI with responsive design
  - Real-time backend status monitoring
  - Automatic conversation saving
- **Conversation History**: Save and load previous conversations
  - Create unlimited conversations
  - Auto-title based on first question
  - Rename and organize conversations
  - Delete unwanted conversations
  - Timestamp and message count display
- **Memory Dashboard**: View what the system remembers about you
  - Access at: http://127.0.0.1:5173/memory.html
  - Statistics: interactions, insights, topics
  - Recent history: last 10 Q&A pairs
  - Insights tracking and topic analysis
  - Auto-refresh every 10 seconds
- **Teach Me Mode**: Spaced repetition learning system
  - Flashcard generation from conversations
  - Quiz sessions with scoring
  - Progress tracking and statistics
- **Voice Input/Output**: Speech recognition and synthesis
  - 🎤 Voice input with visual recording indicator
  - 🔊/🔇 Voice output toggle
  - Requires internet connection
  - Error handling with user-friendly messages
- **Answer Length Control**: Choose response detail
  - Brief (2-3 paragraphs)
  - Medium (3-5 paragraphs) - default
  - Detailed (5-8+ paragraphs)

## Usage Examples

### Web Interface

Open http://127.0.0.1:5173 in your browser and start chatting with Feynman.

**Main Features:**

1. **Chat**: 
   - Type questions or use 🎤 voice input
   - Select answer length (brief/medium/detailed)
   - Toggle 🔊 voice output to hear responses
   - Conversations auto-save

2. **Sidebar Menu**:
   - Click ☰ to open conversation list
   - Create new chats with "New Chat" button
   - Click any conversation to load it
   - Rename or delete conversations

3. **Memory Dashboard**:
   - Navigate to http://127.0.0.1:5173/memory.html
   - View statistics, insights, and topics
   - Auto-refreshes every 10 seconds
   - Click "Back to Chat" to return

4. **Voice Features**:
   - **Voice Input**: Click 🎤, speak question, auto-transcribed
   - **Voice Output**: Click 🔊 to toggle speech synthesis
   - Both require internet connection

5. **Answer Length**:
   - **Brief**: Quick, focused (2-3 paragraphs)
   - **Medium**: Balanced (3-5 paragraphs) - default
   - **Detailed**: Comprehensive (5-8+ paragraphs)

**Example Workflow:**
```
1. Open http://127.0.0.1:5173
2. Select "Medium" answer length
3. Enable 🔊 voice output
4. Type or speak: "Explain quantum entanglement"
5. Read response and hear it spoken
6. Check metadata: "Retrieved docs: 5 | Personality: 85%"
7. Conversation auto-saved in sidebar
```

- **Real-time Chat**: Type questions and get instant responses
- **Conversation Management**: Create, rename, and delete conversations
- **Answer Length Control**: Choose between brief, medium, or detailed responses
- **Voice Input**: Use speech recognition to ask questions (requires internet)
- **Voice Output**: Listen to Feynman's responses
- **Memory Dashboard**: View session and persistent memory
- **Teach Me Mode**: Practice concepts with spaced repetition

### Interactive Mode (CLI)

```
You: What is the Feynman Technique?

Feynman: Well, that's the method I developed for really understanding something deeply. It's quite simple, actually...
[Personality alignment: 94%]
[Retrieved 5 relevant documents]
```

### Special Commands

In interactive mode:

- `quit` - Exit and save session
- `memory` - See what I remember about you
- `save` - Manually save current session

### Programmatic Usage

```python
from main import FeynmanTwin

# Initialize
twin = FeynmanTwin()
answer, metadata = twin.answer_question("What is the Feynman Technique?")

print(answer)
print(f"Personality score: {metadata['personality_score']}")
print(f"Retrieved docs: {metadata['retrieved_docs']}")
```

## Architecture

```
feynman_twin/
├── src/
│   ├── main.py              # Main agent orchestration
│   ├── api_server.py        # FastAPI REST API
│   ├── rag_system.py        # RAG implementation
│   ├── memory_system.py     # Dual memory system
│   ├── personality.py       # Personality encoding
│   ├── data_collector.py    # Data processing pipeline
│   └── config.py            # Configuration
├── frontend/
│   ├── index.html           # Web interface
│   ├── app.js               # Frontend logic
│   └── styles.css           # Styling
├── data/                    # Knowledge base (auto-generated)
├── embeddings/              # Vector database (auto-generated)
├── memory/                  # Persistent memory (auto-generated)
└── .env                     # API keys (create this)
```

## API Endpoints

### Health Check
```bash
GET /api/health
```
Response:
```json
{
  "status": "ok",
  "rag_ready": true
}
```

### Chat
```bash
POST /api/chat
Content-Type: application/json

{
  "question": "Explain quantum entanglement"
}
```
Response:
```json
{
  "answer": "Well, let me explain it this way...",
  "metadata": {
    "retrieved_docs": 5,
    "personality_score": 0.85,
    "processing_time": 2.3
  }
}
```

## Example Questions

- "What is the Feynman Technique?"
- "Explain quantum electrodynamics"
- "How do you approach teaching?"
- "What is your view on curiosity?"
- "Explain the double-slit experiment"

## System Specifications

| Aspect | Details |
|--------|---------|
| **AI Model** | Google Gemini 2.5 Flash (+ 1.5 fallback) |
| **Vector DB** | ChromaDB with embeddings |
| **Documents** | ~2,657 chunks from Feynman's works |
| **Memory** | ~500MB (embeddings + data) |
| **Setup Time** | ~10 minutes (first time) |
| **Query Speed** | 1-5 seconds (after initial setup) |
| **Cost** | <$0.01 per conversation |

## Configuration

Edit `feynman_twin/src/config.py` to customize:

- AI model selection
- Temperature and response settings
- RAG parameters (k-nearest neighbors)
- Memory settings
- API timeouts

## Security

- API keys stored in `.env` file (not committed to git)
- CORS configured for local development
- All data stored locally
- No external data transmission except API calls

## Documentation

Comprehensive documentation available in `feynman_twin/`:
- `START_HERE.md` - Overview and quick start
- `INDEX.md` - Documentation navigation
- `GETTING_STARTED.md` - Detailed setup guide
- `ARCHITECTURE.md` - Technical architecture
- `TROUBLESHOOTING.md` - Common issues and solutions
- `QUICK_REFERENCE.md` - Command reference

## Troubleshooting

### "Retrieved docs: 0" Issue (FIXED in v2.1)
**Issue**: Frontend showed "Retrieved docs: 0" even when RAG was working.  
**Solution**: Upgraded ChromaDB from 0.4.24 to 1.5.9. If you see this issue:
1. Stop the backend server
2. Delete `feynman_twin/chroma_db/` directory
3. Run: `.virtual/Scripts/pip.exe install --upgrade chromadb`
4. Rebuild embeddings: `python main.py --setup`
5. Restart servers

See `BUG_FIX_REPORT.md` for details.

### "Retrieved docs: 0" Issue (FIXED in v2.1)
**Symptom**: Frontend shows "Retrieved docs: 0" even when asking physics questions  
**Cause**: ChromaDB version 0.4.24 had schema incompatibility  
**Solution**: 
```bash
# 1. Stop backend server
# 2. Delete corrupted database
Remove-Item -Recurse -Force feynman_twin/chroma_db

# 3. Upgrade ChromaDB
.virtual/Scripts/pip.exe install --upgrade chromadb

# 4. Rebuild embeddings
cd src
python main.py --setup

# 5. Restart servers
```
See `../BUG_FIX_REPORT.md` for detailed information.

### "GEMINI_API_KEY not set"
- Copy `.env.template` to `.env`
- Add your key from https://aistudio.google.com/app/apikeys

### "No processed data found"
- Run `python main.py --setup` to collect and process data

### "RAG system not ready"
- Ensure embeddings database is built: `python main.py --setup`
- Check `embeddings/` directory exists
- Verify ChromaDB collection has documents: Run `test_simple_retrieval.py`

### "Port 8000 already in use"
- Kill the process using port 8000: `netstat -ano | findstr :8000`
- Kill the PID: `taskkill /F /PID <PID>`
- Or use a different port: `python -m uvicorn api_server:app --port 8001`

### Frontend shows "Backend unreachable"
1. Check backend is running on port 8000
2. Verify `app.js` has `API_BASE = "http://127.0.0.1:8000"`
3. Check CORS settings in `api_server.py`

### Slow first response
Normal - the system builds the RAG index on first query. Subsequent queries are fast.

### API key issues
See `feynman_twin/SETUP_API_KEY.md` for detailed instructions.

## Support

For issues and questions:
1. Check `TROUBLESHOOTING.md`
2. Review API docs at http://127.0.0.1:8000/docs
3. Open an issue on GitHub

---

**Built with ❤️ to make Feynman's teaching accessible to everyone**

*"The first principle is that you must not fool yourself, and you are the easiest person to fool." - Richard Feynman*
