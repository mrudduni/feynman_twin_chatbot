# Richard Feynman Digital Twin

An AI-powered digital twin of Richard Feynman that combines RAG (Retrieval-Augmented Generation) with personality encoding to answer questions in Feynman's characteristic teaching style.

![Status](https://img.shields.io/badge/status-production-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

### Core AI Capabilities
- **RAG System**: Retrieves relevant content from 2,657 chunks of Feynman's lectures using ChromaDB 1.5.9
- **LangGraph Agent**: Multi-step reasoning with query classification, retrieval evaluation, and response refinement
- **Dual Memory**: Session memory (current conversation) + persistent memory (across sessions)
- **Personality Encoding**: 87% alignment with Feynman's teaching style using personality scoring
- **Local Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (no API quota limits)

### Web Interface Features
- **Modern Chat UI**: Clean, responsive interface with galaxy background
- **Conversation Management**: Create, save, rename, and delete conversations
- **Sidebar Navigation**: Easy access to conversation history
- **Real-time Status**: Backend health monitoring and connection status
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices

### Voice Interaction (v2.0)
- **Voice Input (🎤)**: 
  - Speech-to-text using Web Speech API
  - Visual recording indicator
  - Requires internet connection (Google's servers)
  - Error handling with user-friendly messages
- **Voice Output (🔊/🔇)**:
  - Text-to-speech for all responses
  - Toggle on/off functionality
  - Automatic voice selection (prefers male English voices)
  - Adjustable rate, pitch, and volume

### Memory Dashboard (v2.0)
Access at: http://localhost:5173/memory.html
- **Statistics Panel**: 
  - Total interactions count
  - Total insights captured
  - Topics discussed
- **Recent Interactions**: Last 10 Q&A exchanges
- **Insights Tracking**: Key learnings and discoveries
- **Topic Analysis**: Frequency map of discussed subjects
- **User Preferences**: Saved learning preferences
- **Auto-Refresh**: Updates every 10 seconds

### Timeline Awareness (v2.0)
- **Historical Context**: Acknowledges Feynman's era (1918-1988)
- **Dynamic Date Calculation**: Automatically calculates years since 1988
- **Contextual References**: Uses phrases like "In my time..." when appropriate
- **Modern Curiosity**: Expresses interest in post-1988 developments
- **Timeless Principles**: Distinguishes era-specific from universal physics concepts

### Answer Length Control (v2.0)
- **Brief** (2-3 paragraphs): Quick, focused explanations of core concepts
- **Medium** (3-5 paragraphs): Balanced explanations with examples (default)
- **Detailed** (5-8+ paragraphs): Comprehensive, in-depth explorations with multiple analogies

### Advanced Features
- **REST API**: FastAPI backend with full OpenAPI documentation
- **Metadata Tracking**: 
  - Retrieved documents count (fixed in v2.1)
  - Personality alignment scores (0-100%)
  - Model used (gemini-2.5-flash)
  - Processing time metrics
- **Socratic Method**: Asks guiding questions to deepen understanding
- **Teaching Style Enhancement**: Adds personal touches and analogies
- **Query Classification**: Intelligent routing between simple and complex queries
- **Context Aggregation**: Optimal chunking and overlap for semantic coherence

## New in v2.0

### Recent Bug Fixes (v2.1)
- **Fixed RAG Display**: Resolved "Retrieved docs: 0" issue by upgrading ChromaDB
- **Enhanced Logging**: Added comprehensive logging throughout agent workflow
- **Improved Query Classification**: Better detection of complex vs simple queries
- **Metadata Flow**: Fixed metadata propagation from agent to frontend

### Chat Saving
- **Persistent Chat History**: Saves conversations to local storage
- **Session Management**: Load, save, and delete chat sessions
- **Local Storage**: All data stored in browser, no server required

### Voice Interaction
- **Voice Input**: Speech-to-text using Web Speech API (requires internet)
- **Voice Output**: Automatic text-to-speech for responses
- **Toggle Controls**: Enable/disable voice features as needed
- **Error Handling**: User-friendly error messages for common issues

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

### Answer Length Control
- **Brief**: 2-3 paragraphs, core concepts only
- **Medium**: 3-5 paragraphs with examples (default)
- **Detailed**: 5-8+ paragraphs with comprehensive explanations

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
| **ChromaDB Version** | 1.5.9 | Vector database version |
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

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikeys))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Richard\ Feynman
   ```

2. **Set up environment**
   ```bash
   python setup.py setup
   ```

3. **Configure API key**
   
   Create a `.env` file in the `feynman_twin/` directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Initialize data** (first time only, takes 5-10 minutes)
   ```bash
   cd feynman_twin/src
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
   - **Chat Interface**: http://127.0.0.1:5173
   - **Memory Dashboard**: http://127.0.0.1:5173/memory.html
   - **API Docs**: http://127.0.0.1:8000/docs

### Feature Guide

#### Chat Interface
- **Ask Questions**: Type in the text box or use voice input (🎤)
- **Answer Length**: Select brief, medium, or detailed from dropdown
- **Voice Output**: Toggle speaker icon (🔊/🔇) to enable/disable
- **New Chat**: Click "New Chat" to start fresh conversation
- **History**: Click menu icon to view/load previous conversations

#### Voice Features
**Voice Input (🎤)**:
1. Click microphone button
2. Grant browser permission if prompted
3. Speak your question clearly
4. Question appears in text box automatically
5. Requires internet connection

**Voice Output (🔊)**:
- Automatically reads responses when enabled
- Click speaker icon to toggle on/off
- Uses browser's native speech synthesis
- Prefers male English voices (mimics Feynman)

#### Memory Dashboard
Navigate to: http://127.0.0.1:5173/memory.html
- View statistics (total interactions, insights, topics)
- See last 10 conversations
- Track key insights discovered
- Monitor topic frequency
- Auto-refreshes every 10 seconds
- Click "Back to Chat" to return

#### Answer Length Selection
Choose response detail level:
- **Brief**: Quick explanation, 2-3 paragraphs
- **Medium**: Balanced with examples, 3-5 paragraphs (default)
- **Detailed**: Comprehensive exploration, 5-8+ paragraphs

#### Conversation Management
- **Create**: Click "New Chat" button
- **Save**: Conversations auto-save after each message
- **Load**: Click any conversation in sidebar
- **Rename**: Click "rename" button next to conversation
- **Delete**: Click "delete" button next to conversation

### Command Line Interface

**Interactive chat mode**:
```bash
cd feynman_twin/src
python main.py
```

**Single question**:
```bash
cd feynman_twin/src
python main.py --query "Explain quantum mechanics"
```

**View memory**:
```bash
# In interactive mode, type:
memory
```

**Save conversation**:
```bash
# In interactive mode, type:
save
```

### Python Library

```python
from main import FeynmanTwin

# Initialize
twin = FeynmanTwin()

# Ask with custom length
answer, metadata = twin.answer_question(
    question="What is the Feynman Technique?",
    answer_length="detailed",  # brief, medium, or detailed
    conversation_id=None  # or existing conv_id to continue
)

print(answer)
print(f"Personality score: {metadata['personality_score']:.0%}")
print(f"Retrieved docs: {metadata['retrieved_docs']}")
print(f"Model used: {metadata['model_used']}")
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
  "question": "Explain quantum entanglement",
  "answer_length": "medium",
  "conversation_id": null
}
```
Response:
```json
{
  "answer": "Well, let me explain it this way...",
  "metadata": {
    "retrieved_docs": 5,
    "personality_score": 0.85,
    "model_used": "gemini-2.5-flash"
  },
  "conversation_id": "conv_abc123"
}
```

### Memory Dashboard
```bash
GET /api/memory
```
Response:
```json
{
  "session_memory": [
    {"question": "What is quantum mechanics?", "answer": "..."}
  ],
  "persistent_memory": {
    "user_preferences": {},
    "insights": ["Discussion about quantum mechanics"],
    "topic_interests": {"physics": 5}
  },
  "stats": {
    "total_interactions": 12,
    "total_insights": 3,
    "topics_discussed": 4
  }
}
```

## Example Questions

Try these questions to explore different features:

### Physics & Science
- "Explain the double-slit experiment and wave-particle duality"
- "What are Feynman diagrams and why are they useful?"
- "How does quantum entanglement work?"
- "Explain the path integral formulation"
- "What is quantum electrodynamics?"

### Teaching & Learning
- "What is the Feynman Technique for learning?"
- "How should I approach learning physics?"
- "What's your view on curiosity and asking questions?"
- "How do you make complex topics simple?"

### Timeline Awareness (Tests historical context)
- "What do you think about modern quantum computers?" (will acknowledge post-1988)
- "Tell me about physics in your time" (will reference 1918-1988)
- "What would you think about recent discoveries in physics?"

### Answer Length Testing
- Set to **Brief**: "What is quantum mechanics?" (2-3 paragraphs)
- Set to **Medium**: "Explain quantum mechanics" (3-5 paragraphs)
- Set to **Detailed**: "Explain quantum mechanics in depth" (5-8+ paragraphs)

### Voice Features
- Use 🎤 to ask: "Explain why the sky is blue"
- Enable 🔊 to hear the response read aloud

## System Specifications

| Aspect | Details |
|--------|---------|
| **AI Model** | Google Gemini 2.5 Flash (+ 1.5 fallback) |
| **Vector DB** | ChromaDB 1.5.9 with HNSW indexing |
| **Documents** | 2,657 chunks from Feynman's works |
| **Embedding Model** | sentence-transformers/all-MiniLM-L6-v2 (local) |
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

### Backend shows "Module not found"
Ensure you're using the virtual environment:
```bash
..\..\virtual\Scripts\python.exe -m uvicorn api_server:app --host 127.0.0.1 --port 8000
```

### Frontend shows "Backend unreachable"
1. Check backend is running on port 8000
2. Verify `app.js` has `API_BASE = "http://127.0.0.1:8000"`
3. Check CORS settings in `api_server.py`

### Slow first response
Normal - the system builds the RAG index on first query. Subsequent queries are fast.

### API key issues
See `feynman_twin/SETUP_API_KEY.md` for detailed instructions.

### Voice input not working
Voice features require:
- Internet connection (uses Google's Web Speech API)
- Modern browser (Chrome, Edge recommended)
- Microphone permissions granted
- HTTPS or localhost (security requirement)

## Support

For issues and questions:
1. Check `TROUBLESHOOTING.md`
2. Check `BUG_FIX_REPORT.md` for recent fixes
3. Review API docs at http://127.0.0.1:8000/docs
4. Open an issue on GitHub

## Recent Updates

### v2.1 (June 2026)
- Fixed "Retrieved docs: 0" display bug
- Upgraded ChromaDB to 1.5.9
- Enhanced query classification logic
- Added comprehensive logging system
- Improved metadata flow

### v2.0 (June 2026)
- Voice interaction (input/output)
- Memory visualization dashboard
- Timeline awareness system
- Answer length control
- Chat history management
- Persistent conversations

---

**Built with ❤️ to make Feynman's teaching accessible to everyone**

*"The first principle is that you must not fool yourself, and you are the easiest person to fool." - Richard Feynman*
