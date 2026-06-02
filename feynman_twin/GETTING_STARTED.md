# Getting Started with Feynman Digital Twin

## 5-Minute Quick Start

### Step 1: Get Your API Key (1 minute)

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy the generated key

### Step 2: Initial Setup (2 minutes)

**On Windows:**
```batch
cd feynman_twin
run.bat setup
```

**On Mac/Linux:**
```bash
cd feynman_twin
python setup.py setup
```

When prompted, paste your API key.

### Step 3: Collect Data & Build Knowledge (5-10 minutes)

**On Windows:**
```batch
cd src
python main.py --setup
```

**On Mac/Linux:**
```bash
cd src
python main.py --setup
```

This will:
- Download papers from arXiv
- Fetch Wikipedia articles
- Create vector embeddings
- Build the knowledge database

### Step 4: Start Chatting!

**Interactive mode:**
```bash
python main.py
```

**Single question:**
```bash
python main.py --query "What is the Feynman Technique?"
```

---

## Complete Installation Guide

### Requirements

- Python 3.8+
- Internet connection
- Gemini API key (free tier works)
- ~500MB disk space

### Full Setup Process

#### 1. **Prepare**

```bash
# Navigate to project
cd feynman_twin

# Copy environment template
cp .env.template .env  # Mac/Linux
# OR on Windows:
copy .env.template .env
```

#### 2. **Configure API Key**

Edit `.env` file and add your key:

```
GEMINI_API_KEY=your_actual_key_here
```

#### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

This installs:
- `google-generativeai` - Gemini API
- `langchain` - RAG framework
- `chromadb` - Vector database
- `arxiv` - Paper collection
- `wikipedia` - Wikipedia data
- And more...

#### 4. **Initialize RAG System**

```bash
cd src
python main.py --setup
```

Progress indicators:
- ✓ Fetching arXiv papers
- ✓ Fetching Wikipedia content
- ✓ Creating curated knowledge
- ✓ Processing documents
- ✓ Building embeddings

#### 5. **Verify Installation**

```bash
python main.py --query "Hello, who are you?"
```

Expected response starts with something like:
```
I'm Richard Feynman, a physicist and educator...
```

---

## Using the System

### Interactive Conversation

```bash
python main.py
```

Example session:

```
Welcome to the Richard Feynman Digital Twin
======================================

You: What is the double slit experiment?

Feynman: Well, this is one of my favorite experiments because it really 
shows something strange about quantum mechanics...

[Personality alignment: 92%]
[Retrieved 5 relevant documents]

You: memory

Memory Summary:
Total interactions: 1
Top topics: quantum mechanics, experiments

You: quit

Session saved. Goodbye!
```

### Commands

| Command | Effect |
|---------|--------|
| `quit` | Exit and save session |
| `memory` | View what Feynman remembers |
| `save` | Manually save session |
| Any question | Ask Feynman directly |

### Example Questions

**About Physics:**
- "Explain quantum entanglement"
- "What's special about the speed of light?"
- "How do electron clouds work?"
- "What is the uncertainty principle?"

**About Learning:**
- "What is the Feynman Technique?"
- "How do you approach teaching?"
- "What makes a good scientist?"
- "Why is curiosity important?"

**About Science:**
- "What's the most important principle in science?"
- "How do you know if something is true?"
- "What role does imagination play in science?"

**Personal:**
- "What was your biggest breakthrough?"
- "How do you think about problems?"
- "What's your philosophy on learning?"

---

## Programmatic Usage

### Python API

```python
from main import FeynmanTwin

# Initialize
twin = FeynmanTwin()

# Ask a question
response, metadata = twin.answer_question(
    "Explain the Feynman Technique"
)

print(response)
print(f"Personality score: {metadata['personality_score']:.0%}")
```

### Multiple Questions

```python
questions = [
    "What is quantum mechanics?",
    "How do you think about learning?",
    "Explain this with an analogy",
]

results = twin.batch_query(questions)
for r in results:
    print(f"Q: {r['question']}\nA: {r['response']}\n")
```

### Access Memory

```python
# Session memory
history = twin.memory_manager.session_memory.conversation_history

# Persistent memory
facts = twin.memory_manager.persistent_memory.get_learned_facts()
insights = twin.memory_manager.persistent_memory.get_insights()
topics = twin.memory_manager.persistent_memory.data['frequently_discussed_topics']
```

### Load Previous Session

```python
from pathlib import Path

# Load a saved session
session_file = Path("memory/conversations/session_xyz_20240101_120000.json")
twin.memory_manager.load_previous_session(session_file)

# Continue conversation
response, _ = twin.answer_question("Continue explaining quantum mechanics")
```

---

## Demos

Try the demo script to see all capabilities:

```bash
# Run all demos (no API key needed for most)
python demo.py --all

# Run specific demo
python demo.py --demo 1  # Basic QA
python demo.py --demo 2  # Memory systems
python demo.py --demo 3  # Personality analysis
python demo.py --demo 4  # Teaching style
python demo.py --demo 5  # Feynman traits
python demo.py --demo 6  # Batch processing
```

---

## Configuration

### Key Settings (in `src/config.py`)

```python
# Models
PRIMARY_MODEL = "gemini-2.5-flash"      # Fast, efficient
FALLBACK_MODEL = "gemini-1.5-pro"       # Fallback for complex queries

# RAG parameters
CHUNK_SIZE = 1000                       # Document chunk size
CHUNK_OVERLAP = 200                     # Overlap between chunks

# Personality
FEYNMAN_PERSONALITY = {
    "curiosity": 0.95,                  # Very curious
    "humor": 0.85,                      # Humorous
    "clarity": 0.90,                    # Very clear
    "critical_thinking": 0.95,          # Skeptical
    "teaching_style": "socratic",       # Asks questions
}
```

### Data Sources (in `src/config.py`)

```python
FEYNMAN_SOURCES = {
    "arxiv_query": "Richard Feynman physics",  # Papers to fetch
    "wikipedia_pages": [
        "Richard Feynman",
        "Quantum electrodynamics",
        # Add more pages
    ],
}
```

### Adjust Personality

Edit `src/personality.py` to customize:
- System prompts
- Analogies
- Teaching intros
- Socratic questions

---

## Troubleshooting

### API Key Issues

**Error:** `GEMINI_API_KEY not set`

**Solution:**
1. Create `.env` file in project root
2. Add: `GEMINI_API_KEY=your_key`
3. Verify with: `echo $GEMINI_API_KEY` (or check in Windows Settings)

### Data Not Collected

**Error:** `No processed data found`

**Solution:**
```bash
cd src
python main.py --setup
# Wait for completion
```

### Slow First Response

**Issue:** First query takes 30-60 seconds

**Why:** Building vector index on first use

**Solution:** Normal behavior, subsequent queries are fast

### Memory Files Not Saving

**Check:**
1. Does `memory/` directory exist? (Should be auto-created)
2. Write permissions on directory?
3. Disk space available?

**Verify:**
```bash
ls -la memory/  # Mac/Linux
dir memory      # Windows
```

### Model Errors

**Error:** `Model not found` or similar

**Solution:**
1. Verify API key is active
2. Check internet connection
3. Ensure `PRIMARY_MODEL` exists in Gemini API
4. Fallback will auto-activate if primary fails

---

## Performance Tips

### Speed Up First Setup

```bash
# Skip Wikipedia (keep just arXiv + curated)
# Edit src/data_collector.py, comment out Wikipedia collection
```

### Improve Response Quality

- Ask more specific questions
- Use follow-up questions for depth
- Reference previous points in conversation

### Reduce Memory Usage

- Limit `top_k` retrieval in `rag_system.py` (default: 5)
- Reduce `CHUNK_SIZE` if needed
- Archive old conversations

### Cost Optimization

- Gemini 2.5 Flash is very cheap
- Free tier supports ~60 queries/minute
- Each query costs ~$0.00001

---

## Advanced Usage

### Custom Data Sources

Edit `src/data_collector.py`:

```python
def collect_custom_sources(self) -> List[Dict]:
    """Add your own sources"""
    # Implement your collection logic
    pass
```

### Fine-tune Personality

Edit responses in `src/personality.py`:

```python
SYSTEM_PROMPT = """Your custom prompt here"""

ANALOGIES = {
    "topic": "Your custom analogy"
}
```

### Process Custom Documents

```python
from data_collector import DataCollector

collector = DataCollector()
# Manually add documents
collector.raw_data.extend(your_documents)
collector.save_raw_data()
processed = collector.process_documents()
collector.save_processed_data(processed)
```

---

## File Structure Reference

```
feynman_twin/
│
├── src/
│   ├── main.py              # Main agent
│   ├── config.py            # Configuration
│   ├── data_collector.py    # Data collection
│   ├── rag_system.py        # RAG pipeline
│   ├── memory_system.py     # Memory management
│   ├── personality.py       # Personality encoding
│   └── __init__.py
│
├── data/
│   ├── raw/                 # Raw collected data (auto-created)
│   └── processed/           # Processed chunks (auto-created)
│
├── embeddings/              # Vector DB (auto-created, ~100MB)
├── memory/                  # Session & persistent memory (auto-created)
│
├── .env                     # API keys (create from template)
├── .env.template           # Template for .env
├── requirements.txt        # Dependencies
├── setup.py               # Setup script
├── demo.py                # Demo script
├── run.bat                # Windows launcher
└── README.md              # Full documentation
```

---

## Next Steps

1. ✅ Install and setup
2. 📚 Run `python main.py --setup` to collect knowledge
3. 💬 Try interactive mode: `python main.py`
4. 🔬 Experiment with different questions
5. 🧠 Check memory: type `memory` in interactive mode
6. 📝 Load previous sessions from `memory/conversations/`

---

## Support & Questions

Check the [README.md](README.md) for:
- Full API documentation
- Advanced customization
- Performance tuning
- Future enhancements

---

**Enjoy learning with Richard Feynman!**

*"The first principle is that you must not fool yourself, and you are the easiest person to fool."*
