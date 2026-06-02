# Feynman Digital Twin - Quick Reference

## Installation (First Time)

```bash
# Navigate to project
cd feynman_twin

# Setup with automatic dependency installation
python setup.py setup
# OR on Windows:
# run.bat setup

# When prompted, enter your Gemini API key from:
# https://aistudio.google.com/app/apikeys
```

## Initial Data Collection

```bash
cd src
python main.py --setup

# This will:
# ✓ Download papers from arXiv
# ✓ Fetch Wikipedia articles
# ✓ Create curated knowledge
# ✓ Build vector embeddings
# Time: 5-10 minutes
```

## Using Feynman Twin

### Start Interactive Chat
```bash
python main.py
```

### Ask Single Question
```bash
python main.py --query "Your question here"
```

### In Interactive Mode
- **Type question** - Ask normally
- **Type `memory`** - See what Feynman remembers
- **Type `save`** - Manually save session
- **Type `quit`** - Exit and save

## Configuration

### Add API Key
Edit `.env`:
```
GEMINI_API_KEY=your_actual_key
```

### Change Models
Edit `src/config.py`:
```python
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-1.5-pro"
```

### Customize Personality
Edit `src/personality.py`:
```python
FEYNMAN_PERSONALITY = {
    "curiosity": 0.95,
    "humor": 0.85,
    "clarity": 0.90,
}
```

## File Locations

| File | Purpose |
|------|---------|
| `.env` | API credentials |
| `src/main.py` | Main agent |
| `src/config.py` | Settings |
| `src/data_collector.py` | Data collection |
| `src/rag_system.py` | Knowledge retrieval |
| `src/memory_system.py` | Memory management |
| `src/personality.py` | Personality traits |
| `data/raw/` | Raw collected data |
| `data/processed/` | Processed documents |
| `embeddings/` | Vector database |
| `memory/` | Conversation history |

## Programmatic Usage

### Basic Example
```python
from main import FeynmanTwin

twin = FeynmanTwin()
response, metadata = twin.answer_question("Your question")
print(response)
```

### Multiple Questions
```python
questions = ["Q1", "Q2", "Q3"]
results = twin.batch_query(questions)
```

### Check Memory
```python
# Session memory
history = twin.memory_manager.session_memory.conversation_history

# Persistent memory
facts = twin.memory_manager.persistent_memory.get_learned_facts()
```

## Demos

```bash
# Run all demos (offline, no API key needed)
python demo.py --all

# Run specific demo
python demo.py --demo 1  # QA
python demo.py --demo 2  # Memory
python demo.py --demo 3  # Personality
python demo.py --demo 4  # Teaching style
python demo.py --demo 5  # Traits
python demo.py --demo 6  # Batch processing
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key not working | Check .env file, get key from aistudio.google.com |
| No data collected | Run `python main.py --setup` |
| Slow first query | Normal (indexing), subsequent queries fast |
| Memory not saving | Check `memory/` directory permissions |
| Import errors | Run `pip install -r requirements.txt` |

## Performance Tips

- **Faster setup**: Skip Wikipedia collection in `data_collector.py`
- **Cheaper queries**: Use gemini-2.5-flash (default)
- **Better answers**: Ask specific, follow-up questions
- **Faster responses**: Subsequent queries after first

## Example Questions

### Physics
- "Explain quantum mechanics simply"
- "What is the uncertainty principle?"
- "How do electron clouds work?"
- "Explain this with an analogy"

### Learning
- "What is the Feynman Technique?"
- "How do you approach teaching?"
- "Why is understanding important?"
- "What makes a good scientist?"

### Science Philosophy
- "What's the first principle?"
- "How do you know if something is true?"
- "What role does imagination play?"
- "Why is curiosity important?"

## Common Commands

```bash
# Full setup
python setup.py setup

# Collect data and build embeddings
python main.py --setup

# Interactive chat
python main.py

# Single query
python main.py --query "Question"

# View demos
python demo.py --all

# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install -r requirements.txt --upgrade
```

## Keyboard Shortcuts (Interactive Mode)

| Key | Action |
|-----|--------|
| Enter | Send message |
| Ctrl+C | Exit (saves session) |
| Ctrl+D | Exit (saves session) |

## Directory Structure

```
feynman_twin/
├── src/              # Main code
├── data/raw/         # Raw data
├── data/processed/   # Processed chunks
├── embeddings/       # Vector DB
├── memory/           # Sessions & memory
├── .env             # Your API key
├── requirements.txt # Dependencies
├── README.md        # Full docs
└── GETTING_STARTED.md # Setup guide
```

## API Key from Google

1. Visit: https://aistudio.google.com/app/apikeys
2. Click "Create API Key"
3. Copy the key
4. Paste in `.env` file

## Cost Estimate

| Model | Cost | Notes |
|-------|------|-------|
| Gemini 2.5 Flash | $0.01/1M | Primary (cheap) |
| Gemini 1.5 Pro | $1.50/1M | Fallback only |
| Embeddings | Free | Included |

Typical conversation: < $0.01

## Next Steps

1. ✅ Install: `python setup.py setup`
2. 📚 Collect data: `python main.py --setup`
3. 💬 Chat: `python main.py`
4. 🔍 Check memory: type `memory`
5. 📖 Read full docs: See README.md

## Getting Help

1. Check **GETTING_STARTED.md** - Detailed setup guide
2. Check **README.md** - Complete documentation
3. Check **ARCHITECTURE.md** - How it works
4. Check error messages in terminal
5. Verify `.env` file has API key

## Resources

- [Gemini API Docs](https://ai.google.dev/docs)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [LangChain Docs](https://docs.langchain.com/)
- [Feynman Lectures](https://www.feynmanlectures.caltech.edu/)

---

**Pro Tip**: Save interesting conversations from `memory/conversations/` for later review!
