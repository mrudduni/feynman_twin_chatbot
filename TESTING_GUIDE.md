# Testing Guide: Verify RAG System Fix

This guide helps you verify that the "Retrieved docs: 0" bug has been fixed.

## Quick Test (Web Interface)

### Step 1: Open Frontend
1. Navigate to: **http://localhost:5173**
2. You should see the Feynman Twin chat interface

### Step 2: Ask a Physics Question
Try any of these questions:
- "Explain quantum mechanics"
- "What is the double slit experiment?"
- "Tell me about Feynman diagrams"
- "How does quantum entanglement work?"
- "Explain wave-particle duality"

### Step 3: Check Metadata Line
After the response, look for the metadata line at the bottom:
```
Retrieved docs: 5 | Personality: 85%
```

**Expected Results:**
- ✅ **Retrieved docs should be 5** (or another number > 0)
- ✅ Personality score should be between 60-100%
- ✅ Response should be relevant to physics

**If you see "Retrieved docs: 0":**
- ❌ RAG system is not working
- See Troubleshooting section below

## Detailed Test (Command Line)

### Test 1: Direct RAG Retrieval

```bash
cd Richard\ Feynman
.virtual/Scripts/python.exe feynman_twin/src/test_simple_retrieval.py
```

**Expected Output:**
```
Initializing RAG system...
INFO:rag_system:Loaded existing collection: feynman_knowledge
INFO:rag_system:Loaded 2657 documents
Collection has 2657 documents

Query: What is quantum mechanics?
Retrieved 5 documents

✓ SUCCESS: RAG retrieval is working!

First document preview:
  Source: feynman_principles
  Title: Quantum Mechanics Insights
  Relevance: 0.552
  Text preview: Quantum Mechanics Insights...
```

**Success Indicators:**
- ✅ Collection has 2,657 documents
- ✅ Retrieved 5 documents
- ✅ Shows "SUCCESS" message

### Test 2: Agent Metadata Flow

```bash
cd Richard\ Feynman
.virtual/Scripts/python.exe feynman_twin/src/test_agent_metadata.py
```

**Expected Output:**
```
Initializing RAG system...
INFO:rag_system:Loaded existing collection: feynman_knowledge
INFO:rag_system:Loaded 2657 documents
Initializing Memory Manager...

Testing agent with a physics question...
INFO:agent_graph:Query classified as: complex
INFO:agent_graph:Retrieving documents for query: Explain the double slit...
INFO:agent_graph:Retrieved 5 documents
INFO:agent_graph:Generating response with 5 retrieved documents
INFO:agent_graph:Enhancing personality for response. Retrieved docs count: 5
INFO:agent_graph:Final metadata: {'retrieved_docs': 5, ...}

METADATA:
Full metadata object: {'personality_score': 0.6, 'model_used': 'gemini-2.5-flash', 'retrieved_docs': 5}

✓ SUCCESS: retrieved_docs is properly set in metadata!
```

**Success Indicators:**
- ✅ Query classified as "complex"
- ✅ Retrieved 5 documents
- ✅ Metadata shows `retrieved_docs: 5`
- ✅ Shows "SUCCESS" message

## Troubleshooting

### Issue: "ERROR: Collection not initialized"

**Cause**: ChromaDB database is corrupted or missing

**Solution**:
```bash
# Delete corrupted database
Remove-Item -Recurse -Force feynman_twin/chroma_db

# Rebuild embeddings
cd feynman_twin/src
python main.py --setup
```

### Issue: "Retrieved docs: 0" in Web Interface

**Cause**: Backend is using old code or ChromaDB version

**Solution**:
```bash
# 1. Stop backend server (Ctrl+C in terminal)

# 2. Upgrade ChromaDB
.virtual/Scripts/pip.exe install --upgrade chromadb

# 3. Restart backend
cd feynman_twin/src
..\..\virtual\Scripts\python.exe -m uvicorn api_server:app --host 127.0.0.1 --port 8000 --reload
```

### Issue: Query classified as "simple" instead of "complex"

**Cause**: Query is too generic (e.g., "What is quantum mechanics?")

**Solution**: Ask more specific questions:
- ❌ "What is quantum mechanics?" (might be classified as simple)
- ✅ "Explain the mathematical foundations of quantum mechanics" (will be complex)
- ✅ "How does the double slit experiment demonstrate wave-particle duality?" (will be complex)

### Issue: API Quota Exceeded

**Cause**: Hit Gemini API daily limit (20 requests for free tier)

**Solution**: Wait until quota resets, or use local embeddings:
```bash
# In .env file, add:
EMBEDDING_BACKEND=local
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Verification Checklist

Use this checklist to verify everything is working:

### Backend Status
- [ ] Backend running on http://127.0.0.1:8000
- [ ] GET /api/health returns `{"status":"ok","rag_ready":true}`
- [ ] No errors in backend terminal

### ChromaDB Status
- [ ] Directory `feynman_twin/chroma_db/` exists
- [ ] Collection has 2,657 documents
- [ ] test_simple_retrieval.py shows SUCCESS

### Agent Status
- [ ] test_agent_metadata.py shows SUCCESS
- [ ] Queries classified correctly (physics = complex)
- [ ] Metadata includes retrieved_docs count
- [ ] Retrieved docs count > 0

### Frontend Status
- [ ] Frontend accessible at http://localhost:5173
- [ ] Chat interface loads correctly
- [ ] Can send messages
- [ ] Metadata line shows "Retrieved docs: 5" (or > 0)

### End-to-End Flow
- [ ] Ask physics question in web interface
- [ ] Receive relevant response
- [ ] Metadata shows retrieved_docs > 0
- [ ] Personality score between 60-100%

## Success Criteria

**✅ All Systems Working** when:
1. test_simple_retrieval.py shows SUCCESS
2. test_agent_metadata.py shows SUCCESS
3. Web interface shows "Retrieved docs: 5" (or similar)
4. Responses are relevant and in Feynman's style

## Getting Help

If tests fail:
1. Check `BUG_FIX_REPORT.md` for detailed fix information
2. Review backend terminal logs for errors
3. Verify ChromaDB version: `.virtual/Scripts/pip.exe show chromadb` (should be 1.5.9)
4. Check `.env` file has valid GEMINI_API_KEY

## Expected Performance

After successful fix:
- **Query Classification**: ~200ms
- **Document Retrieval**: ~120ms  
- **Response Generation**: ~1-3s
- **Total Query Time**: ~2-5s

**First query after restart**: ~30-60s (building index)

---

**Status**: After following this guide, you should see "Retrieved docs: 5" in the frontend! 🎉
