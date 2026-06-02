# Feynman Digital Twin - Installation Checklist & Verification

Use this checklist to verify your installation is working correctly.

## ✅ Pre-Installation Checklist

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Internet connection available
- [ ] ~500MB disk space available
- [ ] Gemini API key from https://aistudio.google.com/app/apikeys
- [ ] Text editor for .env file

## ✅ Installation Checklist

### Step 1: Setup Environment
- [ ] Navigate to `feynman_twin/` directory
- [ ] Run `python setup.py setup`
- [ ] Created `.env` file
- [ ] Added GEMINI_API_KEY to `.env`
- [ ] No errors during setup

**Verify:**
```bash
python -c "import os; print(os.getenv('GEMINI_API_KEY')[:10])"
# Should output: AIzaSy... (first 10 chars of key)
```

### Step 2: Install Dependencies
- [ ] All packages installed from requirements.txt
- [ ] No error messages
- [ ] Pip shows successful completion

**Verify:**
```bash
python -c "import chromadb; import google.generativeai; print('✓ Core packages OK')"
```

### Step 3: Directory Structure
- [ ] `src/` directory exists with 6 Python files
- [ ] `data/` directory created
- [ ] `embeddings/` directory created
- [ ] `memory/` directory created
- [ ] `.env` file exists with API key

**Verify:**
```bash
ls -la  # Mac/Linux
dir     # Windows
# Should show: src/, data/, embeddings/, memory/, .env
```

## ✅ Data Collection Checklist

### Initialize RAG System
- [ ] In `src/` directory
- [ ] Run `python main.py --setup`
- [ ] arXiv papers downloaded
- [ ] Wikipedia content fetched
- [ ] Curated knowledge created
- [ ] Documents processed (chunks created)
- [ ] Embeddings built (index created)
- [ ] No errors during collection

**Verify:**
```bash
ls data/raw/
# Should show: feynman_raw_data.json

ls data/processed/
# Should show: feynman_processed_chunks.json

ls embeddings/
# Should show: multiple ChromaDB files
```

**Expected times:**
- Data collection: 3-5 minutes
- Embedding generation: 2-5 minutes
- Total: 5-10 minutes

## ✅ Functionality Verification

### Test 1: Single Query
```bash
cd src
python main.py --query "Who are you?"
```

Expected output:
- ✓ Response starts with "I'm Richard Feynman..."
- ✓ 3-5 retrieved documents mentioned
- ✓ Personality alignment score shown
- ✓ No errors

### Test 2: Interactive Mode
```bash
python main.py
```

Expected output:
- ✓ Welcome message displays
- ✓ Prompt waiting for input
- ✓ Can type questions
- ✓ Responses appear
- ✓ Can type `memory` and see results
- ✓ Can type `quit` to exit
- ✓ Session saved message appears

### Test 3: Demo Suite
```bash
python demo.py --all
```

Expected output:
- ✓ Multiple demo sections run
- ✓ Personality analysis scores shown
- ✓ Teaching style examples displayed
- ✓ No API key required for most demos
- ✓ All demos complete successfully

### Test 4: Memory System
```bash
cd ..  # Back to feynman_twin/
ls memory/
```

Expected output:
- ✓ `persistent_memory.json` exists
- ✓ `conversations/` directory exists
- ✓ Session files created (if you've run interactive mode)

## ✅ Performance Verification

### Timing Checks

First query after setup:
```bash
# Should take 30-60 seconds
# (Building index for first time)
time python main.py --query "Test"
```

Subsequent queries:
```bash
# Should take 1-5 seconds
time python main.py --query "Test"
```

If first query is instant, RAG isn't ready yet. Run:
```bash
python main.py --setup
```

### Memory Usage Check

```bash
# Check embeddings database size
du -sh embeddings/  # Mac/Linux
# Should be ~50-100MB

# Check data files
du -sh data/        # Mac/Linux
# Should be ~10-30MB
```

### Storage Verification

```bash
# Before setup
du -sh feynman_twin/  # ~100MB

# After setup and first run
du -sh feynman_twin/  # ~200-300MB
```

## ✅ Configuration Verification

### .env File
- [ ] File exists in `feynman_twin/` directory
- [ ] Contains `GEMINI_API_KEY=AIzaSy...`
- [ ] No quotes around key
- [ ] No extra spaces
- [ ] One key per line

**Correct format:**
```
GEMINI_API_KEY=AIzaSyDummyExampleKey123456789
```

**Incorrect format:**
```
GEMINI_API_KEY = AIzaSy...     # Extra spaces
GEMINI_API_KEY="AIzaSy..."     # Quotes
GEMINI_API_KEY=AIzaSy... # Extra comment
```

### config.py Settings
- [ ] Models configured
- [ ] Paths correct
- [ ] Personality settings reasonable
- [ ] RAG parameters set

**Verify:**
```bash
cd src
python -c "from config import PRIMARY_MODEL, CHUNK_SIZE; print(f'Model: {PRIMARY_MODEL}, Chunk: {CHUNK_SIZE}')"
# Should output: Model: gemini-2.5-flash, Chunk: 1000
```

## ✅ Common Issues & Fixes

### Issue: "No API Key"
- [ ] Check `.env` file exists
- [ ] Check API key is correct
- [ ] Check no extra spaces or quotes
- [ ] Restart terminal
- [ ] Run: `python setup.py setup` again

### Issue: "Module not found"
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Check you're in correct directory
- [ ] Restart Python interpreter
- [ ] Check `src/` directory exists

### Issue: "No processed data"
- [ ] Run: `python main.py --setup`
- [ ] Check `data/processed/` directory created
- [ ] Check internet connection
- [ ] Check disk space (need ~500MB)

### Issue: "Slow responses"
- [ ] First query always slower (builds index)
- [ ] Subsequent queries should be fast
- [ ] Check internet connection
- [ ] Check API key valid
- [ ] Check disk not full

### Issue: "Memory not saving"
- [ ] Check `memory/` directory writable
- [ ] Check disk space available
- [ ] Run: `ls -la memory/` to see permissions
- [ ] Check JSON files can be created

## ✅ Full System Test Checklist

Complete this test sequence to verify everything works:

```bash
# 1. Navigate to project
cd feynman_twin
echo "✓ Step 1: Navigated to project"

# 2. Check environment
python -c "import os; print(f'✓ Step 2: API Key set: {bool(os.getenv(\"GEMINI_API_KEY\"))}')"

# 3. Check dependencies
python -c "import chromadb; import google.generativeai; print('✓ Step 3: Dependencies OK')"

# 4. Test data collection (first time only)
cd src
python main.py --setup
echo "✓ Step 4: Data collected and embedded"

# 5. Test single query
python main.py --query "Explain the Feynman Technique"
echo "✓ Step 5: Single query works"

# 6. Test interactive mode (type 'quit' to exit)
python main.py
echo "✓ Step 6: Interactive mode works"

# 7. Verify memory saved
cd ..
ls -la memory/conversations/
echo "✓ Step 7: Session saved"
```

## ✅ Verification Summary

Copy this after verifying everything:

```
✅ VERIFICATION COMPLETE

Date: _______
Machine: _______
Python Version: _______

Tests Passed:
- [ ] Installation
- [ ] Configuration
- [ ] Data Collection
- [ ] Single Query
- [ ] Interactive Mode
- [ ] Demo Suite
- [ ] Memory System
- [ ] Performance

Status: READY TO USE ✓
```

## 📊 Expected System State After Setup

| Component | Status | Location |
|-----------|--------|----------|
| Python modules | 6 files | `src/` |
| API Key | Configured | `.env` |
| Raw data | ~20MB | `data/raw/` |
| Processed data | ~30MB | `data/processed/` |
| Embeddings | ~100MB | `embeddings/` |
| Memory | JSON files | `memory/` |
| Documentation | 8 files | root |

## 🎯 Readiness Assessment

### Green Light (Ready)
- ✅ All checklist items completed
- ✅ Test queries work
- ✅ Interactive mode runs
- ✅ Memory files created
- ✅ < 10 second response time

### Yellow Light (Need Help)
- ⚠️ Some tests skipped
- ⚠️ Slow responses
- ⚠️ Memory issues
→ See [TROUBLESHOOTING](README.md#troubleshooting)

### Red Light (Not Ready)
- ❌ API key not working
- ❌ Dependencies missing
- ❌ Data not collected
→ Run `python setup.py setup` again

## 🚀 You're Ready When

1. ✓ All setup steps completed without errors
2. ✓ API key configured correctly
3. ✓ Data collection finished
4. ✓ Single query test passed
5. ✓ Interactive mode launched successfully
6. ✓ Memory files created

## 🎓 Next Steps After Verification

1. Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
2. Try example questions from [GETTING_STARTED.md](GETTING_STARTED.md)
3. Explore `memory/conversations/` to see saved chats
4. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand system
5. Customize `src/personality.py` for variations

---

**Status**: Ready to verify ✅

Print this checklist and check off items as you complete them!
