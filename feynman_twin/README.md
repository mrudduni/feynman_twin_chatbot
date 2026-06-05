# Richard Feynman Digital Twin

A sophisticated AI system that recreates Richard Feynman's unique teaching style and deep physics knowledge. Ask questions about physics, science, learning, or any topic, and receive responses that capture Feynman's characteristic clarity, curiosity, and humor.

## Features

**RAG-Powered Knowledge Base**
- Retrieval-Augmented Generation using ChromaDB 1.5.9 for semantic search
- Automatically collects materials from textbooks and curated sources
- Maintains Feynman's original ideas and perspectives
- Local embeddings using sentence-transformers (no API quota limits)

**LangGraph Multi-Step Reasoning**
- Advanced agent orchestration using LangGraph 0.4.0+
- Multi-step reasoning workflow with query classification
- Retrieval evaluation and response refinement
- Automatic fallback to simple RAG if agent fails

**Dual Memory Systems**
- **Session Memory**: Tracks conversation history within a session
- **Persistent Memory**: Learns about you across sessions, remembers discussed topics
- Automatically saves conversations for future reference

**Feynman's Teaching Style**
- Socratic method: Asks questions to guide understanding
- Clear explanations with everyday analogies
- Encourages curiosity and critical thinking
- Maintains humility about the limits of knowledge

**Multi-turn Conversations**
- Full context awareness of previous messages
- Personality consistency throughout
- Adaptive responses based on discussion history

**Gemini Integration**
- Primary: Gemini 2.5 Flash (faster, efficient)
- Fallback: Gemini 1.5 Flash (for complex queries)
- Automatic failover if primary is unavailable

**New in v2.1**
- Fixed "Retrieved docs: 0" display bug (ChromaDB upgrade)
- Enhanced query classification for better RAG triggering
- Comprehensive logging system
- Voice interaction with speech recognition/synthesis
- Memory visualization dashboard
- Answer length control (brief/medium/detailed)
- Timeline awareness (acknowledges Feynman's era)

## Project Structure

```
feynman_twin/
├── src/
│   ├── main.py              # Main agent orchestrator
│   ├── api_server.py        # FastAPI web server
│   ├── config.py            # Configuration and paths
│   ├── data_collector.py    # Automated data collection
│   ├── rag_system.py        # RAG pipeline with embeddings
│   ├── memory_system.py     # Session and persistent memory
│   ├── personality.py       # Feynman's personality encoding
│   ├── chat_history.py      # Conversation history management
│   ├── teach_me.py          # Spaced repetition learning system
│   └── agent_graph.py       # LangGraph reasoning agent
├── frontend/
│   ├── index.html           # Main web interface
│   ├── app.js               # Frontend JavaScript
│   ├── styles.css           # Styling
│   ├── memory.html          # Memory dashboard
│   └── teach_me.html        # Learning mode interface
├── data/
│   ├── raw/                 # Raw collected data
│   ├── processed/           # Processed chunks for embeddings
│   └── markdown/            # OCR-converted PDFs
├── embeddings/              # ChromaDB vector database
├── memory/                  # Memory files and conversation history
├── requirements.txt         # Python dependencies
├── run_web.bat              # Windows script to start web application
├── .env                     # Environment variables (API keys)
├── .env.template           # Environment variables template
└── README.md               # This file
```

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

This will:
- Fetch Wikipedia articles about Feynman and key concepts
- Extract textbook PDFs 
- Create curated knowledge base from Feynman's principles
- Build vector embeddings database with ChromaDB
- Process everything into searchable chunks

**This takes 5-10 minutes on first run.**

### 3. Start Interactive Session

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

# Ask a question
response, metadata = twin.answer_question(
    "What's the difference between classical and quantum mechanics?"
)

print(response)
print(f"Personality score: {metadata['personality_score']:.0%}")
```

### API Endpoints

The web interface uses the following API endpoints (running on port 8000):

**Chat & Conversations:**
- `POST /api/chat` - Send a question and get a response
- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create a new conversation
- `GET /api/conversations/{id}` - Get a specific conversation
- `DELETE /api/conversations/{id}` - Delete a conversation
- `PATCH /api/conversations/{id}` - Rename a conversation

**Memory & Learning:**
- `GET /api/memory` - Get current memory state
- `GET /api/teach-me/stats` - Get learning statistics
- `POST /api/teach-me/start` - Start a quiz session
- `POST /api/teach-me/answer` - Submit a quiz answer
- `GET /api/teach-me/cards` - Get all flashcards
- `DELETE /api/teach-me/cards/{id}` - Delete a flashcard

**System:**
- `GET /api/health` - Health check and RAG status

## How It Works

### 1. Data Collection Pipeline

```
Sources: arXiv papers, Wikipedia, Curated facts
    ↓
Data Collector (automatic aggregation)
    ↓
Raw Data Storage (JSON)
    ↓
Text Chunking & Processing
    ↓
Processed Chunks (optimized for embeddings)
```

### 2. LangGraph Agent + RAG System

```
User Question
    ↓
LangGraph Agent (Multi-Step Reasoning)
    ├─→ Step 1: Query Classification
    │   (simple/complex/multi_part)
    ├─→ Step 2: Embedding Generation (Gemini)
    ├─→ Step 3: Vector Similarity Search (ChromaDB)
    │   (Top 5 Relevant Documents)
    ├─→ Step 4: Retrieval Evaluation
    │   (Check relevance, decide if re-retrieval needed)
    ├─→ Step 5: Response Generation
    │   (Context + Question → Gemini Model)
    └─→ Step 6: Response Refinement
        (Apply Feynman's teaching style)
    ↓
Feynman-styled Response
    ↓
[Fallback to Simple RAG if Agent Fails]
```

**LangGraph State Management:**
- Maintains conversation state across reasoning steps
- Tracks query type, retrieval attempts, and document quality
- Supports iterative refinement and re-retrieval
- Preserves message history for context awareness

### 3. Memory Systems

**Session Memory:**
- Conversation history within current session
- Topics discussed in order
- Context state for multi-turn conversations

**Persistent Memory:**
- User profile (interests, learning style)
- Frequently discussed topics over time
- Key insights and learned facts
- Interaction count and preferences

### 4. Personality System

The Twin maintains Feynman's characteristics through:
- System prompts emphasizing clarity and curiosity
- Socratic method integration
- Teaching style enhancement
- Personality alignment scoring (0-100%)
- Dynamic response refinement

## Configuration

Edit `src/config.py` to customize:

```python
# Model selection
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-1.5-pro"

# RAG parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Personality weights
FEYNMAN_PERSONALITY = {
    "curiosity": 0.95,
    "humor": 0.85,
    "clarity": 0.90,
    "critical_thinking": 0.95,
    "teaching_style": "socratic",
}

# Data sources
FEYNMAN_SOURCES = {
    "arxiv_query": "Richard Feynman physics",
    "wikipedia_pages": ["Richard Feynman", "Quantum electrodynamics"],
}
```

## Memory Persistence

**Session Memory:**
- Location: `memory/conversations/session_[ID]_[timestamp].json`
- Saved automatically when you exit
- Contains full conversation history and topics

**Persistent Memory:**
- Location: `memory/persistent_memory.json`
- Persists across all sessions
- Tracks user profile, insights, and preferences

Load previous sessions:

```python
from memory_system import MemoryManager
from pathlib import Path

manager = MemoryManager()
manager.load_previous_session(Path("memory/conversations/session_xyz.json"))
```

## Customization

### Add Custom Knowledge Sources

Edit `src/data_collector.py`:

```python
def collect_custom_papers(self) -> List[Dict]:
    """Add your own paper sources"""
    papers = []
    # Add your sources here
    return papers
```

### Modify Personality Traits

Edit `src/personality.py`:

```python
SYSTEM_PROMPT = """Custom prompt emphasizing different traits..."""

ANALOGIES = {
    "your_topic": "your custom analogy",
}
```

### Adjust Teaching Style

Edit `src/personality.py` `TeachingStyler` class:

```python
@staticmethod
def make_socratic(response: str) -> str:
    # Customize Socratic method
    pass
```

## Troubleshooting

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

### "ModuleNotFoundError: No module named 'langchain_google_genai'"
- Install missing dependency: `pip install langchain-google-genai`

### Backend won't start
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.8+
- Check the .env file has valid API key

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_BASE in frontend/app.js is correct (http://127.0.0.1:8000)

### Slow responses initially
- First query builds embedding index, takes 30-60 seconds
- Subsequent queries are much faster (1-5 seconds)

### Voice input not working
- Requires internet connection (uses Google's Web Speech API)
- Modern browser needed (Chrome, Edge recommended)
- Grant microphone permissions
- Must use HTTPS or localhost

### Memory not persisting
- Check `memory/` directory has write permissions
- Verify JSON files are being created

## Personality Tuning

The system includes personality alignment scoring:

```python
from personality import PersonalityAnalyzer

score = PersonalityAnalyzer.score_feynman_alignment(response)
# 0.0-0.4: Doesn't sound like Feynman
# 0.4-0.6: Okay, could be better
# 0.6-0.8: Good Feynman style
# 0.8-1.0: Excellent Feynman style
```

## Advanced Usage

### Batch Processing

```python
questions = [
    "What is quantum entanglement?",
    "Explain the double slit experiment",
    "Why is learning important?",
]

results = twin.batch_query(questions)
for result in results:
    print(f"Q: {result['question']}")
    print(f"A: {result['response']}\n")
```

### Custom Memory Analysis

```python
# Get learned facts
facts = twin.memory_manager.persistent_memory.get_learned_facts()

# Get top topics
topics = twin.memory_manager.persistent_memory.data.get(
    "frequently_discussed_topics"
)

# Get stored insights
insights = twin.memory_manager.persistent_memory.get_insights()
```

## Performance Notes

- **Setup time**: 5-10 minutes (one-time)
- **First query**: 30-60 seconds (building index)
- **Subsequent queries**: 1-5 seconds
- **Memory usage**: ~500MB for full embeddings
- **Storage**: ~100MB for data + embeddings

## API Costs

Using Gemini API:
- **Gemini 2.5 Flash**: Very cheap (~$0.01 per million input tokens)
- **Gemini 1.5 Pro**: Cheap (~$1.50 per million input tokens, fallback only)
- **Embeddings**: Free with Gemini

A typical conversation costs < $0.01.

## Limitations

- Limited to Feynman's public materials
- Cannot learn new information beyond training
- Personality is algorithmic, not truly conscious
- Knowledge cutoff based on collected sources
- Requires internet for data collection

## References

- Feynman, R. P., "Surely You're Joking, Mr. Feynman!"
- Feynman, R. P., "What Do You Care What Other People Think?"
- Feynman, R. P., "The Pleasure of Finding Things Out"
- Feynman Lectures on Physics

## License

Educational and personal use. Respect Richard Feynman's legacy.

## Contributing

Feel free to:
- Add more data sources
- Improve personality encoding
- Enhance memory systems
- Optimize performance
- Report bugs and suggestions

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review `../BUG_FIX_REPORT.md` for recent fixes
3. Check error logs in terminal output
4. Verify .env configuration
5. Test RAG system: Run `src/test_simple_retrieval.py`

## Recent Updates

### v2.1 (June 2026)
- **Fixed**: "Retrieved docs: 0" display bug
- **Upgraded**: ChromaDB from 0.4.24 to 1.5.9
- **Added**: LangGraph 0.4.0+ multi-step reasoning agent
- **Enhanced**: Query classification logic with LangGraph state management
- **Added**: Comprehensive logging throughout agent workflow
- **Improved**: Metadata flow from agent to frontend
- **Added**: Automatic fallback from LangGraph to simple RAG

### v2.0 (June 2026)
- Voice interaction (speech-to-text and text-to-speech)
- Memory visualization dashboard
- Timeline awareness system
- Answer length control
- Chat history management
- Persistent conversations

---

**Made with curiosity and respect for Richard Feynman's legacy of clear thinking and joyful discovery.**
