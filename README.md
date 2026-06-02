# 🎓 Richard Feynman Digital Twin

An AI-powered digital twin of Richard Feynman that combines RAG (Retrieval-Augmented Generation) with personality encoding to answer questions in Feynman's characteristic teaching style.

![Status](https://img.shields.io/badge/status-production-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- 🧠 **RAG System**: Retrieves relevant content from Feynman's lectures and works
- 💬 **Dual Memory**: Session memory + persistent memory across conversations
- 🎭 **Personality Encoding**: Responds in Feynman's unique teaching style
- 🌐 **Web Interface**: Modern, intuitive chat interface
- 🔌 **REST API**: FastAPI backend for easy integration
- 📊 **Metadata Tracking**: Personality scores and retrieval metrics
- 🎯 **Socratic Method**: Guides learning through questions

## 🚀 Quick Start

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

## 🎮 Usage

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

twin = FeynmanTwin()
answer, metadata = twin.answer_question("What is the Feynman Technique?")

print(answer)
print(f"Personality score: {metadata['personality_score']}")
print(f"Retrieved docs: {metadata['retrieved_docs']}")
```

## 🏗️ Architecture

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

## 🔌 API Endpoints

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

## 🎯 Example Questions

- "What is the Feynman Technique?"
- "Explain quantum electrodynamics"
- "How do you approach teaching?"
- "What is your view on curiosity?"
- "Explain the double-slit experiment"

## 📊 System Specifications

| Aspect | Details |
|--------|---------|
| **AI Model** | Google Gemini 2.0 Flash (+ 1.5 Pro fallback) |
| **Vector DB** | ChromaDB with embeddings |
| **Documents** | ~2,657 chunks from Feynman's works |
| **Memory** | ~500MB (embeddings + data) |
| **Setup Time** | ~10 minutes (first time) |
| **Query Speed** | 1-5 seconds (after initial setup) |
| **Cost** | <$0.01 per conversation |

## 🛠️ Configuration

Edit `feynman_twin/src/config.py` to customize:

- AI model selection
- Temperature and response settings
- RAG parameters (k-nearest neighbors)
- Memory settings
- API timeouts

## 🔒 Security

- API keys stored in `.env` file (not committed to git)
- CORS configured for local development
- All data stored locally
- No external data transmission except API calls

## 📝 Documentation

Comprehensive documentation available in `feynman_twin/`:
- `START_HERE.md` - Overview and quick start
- `INDEX.md` - Documentation navigation
- `GETTING_STARTED.md` - Detailed setup guide
- `ARCHITECTURE.md` - Technical architecture
- `TROUBLESHOOTING.md` - Common issues and solutions
- `QUICK_REFERENCE.md` - Command reference

## 🐛 Troubleshooting

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

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional source documents
- Enhanced personality traits
- Web interface improvements
- Multi-modal support (images, diagrams)
- Voice interface

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Richard Feynman's lectures and writings
- Google Gemini API
- ChromaDB for vector storage
- FastAPI framework

## 📞 Support

For issues and questions:
1. Check `TROUBLESHOOTING.md`
2. Review API docs at http://127.0.0.1:8000/docs
3. Open an issue on GitHub

---

**Built with ❤️ to make Feynman's teaching accessible to everyone**

*"The first principle is that you must not fool yourself, and you are the easiest person to fool." - Richard Feynman*
