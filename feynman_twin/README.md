# Richard Feynman Digital Twin

A sophisticated AI system that recreates Richard Feynman's unique teaching style and deep physics knowledge. Ask questions about physics, science, learning, or any topic, and receive responses that capture Feynman's characteristic clarity, curiosity, and humor.

## Features

**RAG-Powered Knowledge Base**
- Retrieval-Augmented Generation using ChromaDB for semantic search
- Automatically collects materials from textbooks and curated sources
- Maintains Feynman's original ideas and perspectives

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
- Fallback: Gemini 1.5 Pro (for complex queries)
- Automatic failover if primary is unavailable

## Project Structure

```
feynman_twin/
├── src/
│   ├── main.py              # Main agent orchestrator
│   ├── config.py            # Configuration and paths
│   ├── data_collector.py    # Automated data collection
│   ├── rag_system.py        # RAG pipeline with embeddings
│   ├── memory_system.py     # Session and persistent memory
│   └── personality.py       # Feynman's personality encoding
├── data/
│   ├── raw/                 # Raw collected data
│   └── processed/           # Processed chunks for embeddings
├── embeddings/              # ChromaDB vector database
├── memory/                  # Memory files and conversation history
├── requirements.txt         # Python dependencies
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
- Collect papers from arXiv about Feynman and quantum mechanics
- Fetch Wikipedia articles about Feynman and key concepts
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

## Usage Examples

### Interactive Mode

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

### 2. RAG System

```
User Question
    ↓
Embedding Generation (Gemini)
    ↓
Vector Similarity Search (ChromaDB)
    ↓
Top 5 Relevant Documents Retrieved
    ↓
Context + Question → Gemini Model
    ↓
Feynman-styled Response
```

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

### "GEMINI_API_KEY not set"
- Copy `.env.template` to `.env`
- Add your key from https://aistudio.google.com/app/apikeys

### "No processed data found"
- Run `python main.py --setup` to collect and process data

### "RAG system not ready"
- Ensure embeddings database is built: `python main.py --setup`
- Check `embeddings/` directory exists

### Slow responses initially
- First query builds embedding index, takes 30-60 seconds
- Subsequent queries are much faster (1-5 seconds)

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

## Future Enhancements

- [ ] Voice interaction support
- [ ] Real-time arXiv paper ingestion
- [ ] Multi-language support
- [ ] Fine-tuned model on Feynman corpus
- [ ] Graphical user interface
- [ ] PDF paper parsing
- [ ] Citation tracking
- [ ] Collaborative learning sessions

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
1. Check the Troubleshooting section
2. Review error logs in terminal output
3. Check memory files for system state
4. Verify .env configuration

---

**Made with curiosity and respect for Richard Feynman's legacy of clear thinking and joyful discovery.**
