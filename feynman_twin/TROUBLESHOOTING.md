# Feynman Digital Twin - Troubleshooting Guide

## 🆘 Quick Problem Solver

**What's your issue?**

1. [I can't install](#installation-issues)
2. [API key isn't working](#api-key-issues)
3. [No data is being collected](#data-collection-issues)
4. [Responses are slow](#performance-issues)
5. [Memory not working](#memory-issues)
6. [Errors running code](#runtime-errors)

---

## Installation Issues

### "Module not found" or Import errors

**Problem**: `ModuleNotFoundError: No module named 'chromadb'`

**Solutions** (try in order):

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Check Python version**
   ```bash
   python --version
   # Needs to be 3.8 or higher
   ```

3. **Use correct Python**
   ```bash
   python3 -m pip install -r requirements.txt
   python3 main.py
   # On some systems, use python3 instead of python
   ```

4. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Reinstall packages**
   ```bash
   pip uninstall chromadb google-generativeai langchain
   pip install -r requirements.txt --force-reinstall
   ```

### "Permission denied" on setup.py

**Solutions**:

```bash
# Mac/Linux - add execute permission
chmod +x setup.py
python setup.py setup

# Or run directly
python setup.py setup
```

### Can't find "setup.py"

**Check location**:
```bash
# Make sure you're in feynman_twin directory
pwd  # Mac/Linux
cd   # Windows
# Should show: .../feynman_twin

# Check file exists
ls setup.py  # Mac/Linux
dir setup.py # Windows
```

---

## API Key Issues

### "GEMINI_API_KEY not set"

**Problem**: System can't find your API key

**Check these (in order)**:

1. **Does .env file exist?**
   ```bash
   ls -la .env  # Mac/Linux
   dir .env     # Windows
   ```
   
   If not:
   ```bash
   cp .env.template .env  # Mac/Linux
   copy .env.template .env # Windows
   ```

2. **Edit .env correctly**
   ```bash
   # Open in text editor and check:
   # Should contain: GEMINI_API_KEY=AIzaSy...
   # NOT: GEMINI_API_KEY = AIzaSy...  (extra space)
   # NOT: GEMINI_API_KEY="AIzaSy..." (quotes)
   ```

3. **Check formatting**
   ```bash
   # Should be exactly:
   GEMINI_API_KEY=your_key_here
   
   # BAD formatting:
   GEMINI_API_KEY = your_key_here    # spaces
   GEMINI_API_KEY="your_key"         # quotes
   GEMINI_API_KEY = 'your_key'       # quotes
   ```

4. **Restart terminal**
   ```bash
   # Close and reopen terminal after editing .env
   # The environment variables need to reload
   ```

5. **Test the key**
   ```bash
   python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
   # Should print your key
   ```

### "Invalid API key"

**Problem**: Key format is wrong or key is inactive

**Solutions**:

1. **Get a new key**
   - Visit https://aistudio.google.com/app/apikeys
   - Delete old key
   - Create new key
   - Copy the new key

2. **Verify key format**
   ```bash
   # Key should:
   # - Start with "AIzaSy"
   # - Be ~40 characters
   # - Have no spaces
   # - Have no extra characters
   ```

3. **Update .env**
   ```bash
   # Edit .env with new key
   # Make sure EXACTLY:
   GEMINI_API_KEY=AIzaSyYourNewKeyHere123456
   # No extra spaces, quotes, or characters
   ```

4. **Restart and test**
   ```bash
   # Close terminal
   # Reopen terminal
   python -c "from main import FeynmanTwin; print('✓ API working')"
   ```

### "Can't generate embeddings"

**Problem**: API works but embedding fails

**Solutions**:

1. **Check API has embeddings enabled**
   - Go to https://aistudio.google.com/app/apikeys
   - Check your key is enabled
   - May need to enable Generative Language API

2. **Try fallback**
   - Edit `src/config.py`
   - Change: `PRIMARY_MODEL = "gemini-1.5-pro"`
   - Test again

3. **Check quota**
   - Visit Google Cloud Console
   - Check API quotas aren't exceeded
   - Free tier has high limits but may have daily cap

---

## Data Collection Issues

### "No processed data found"

**Problem**: Data collection hasn't run

**Solution**:
```bash
cd src
python main.py --setup
# Wait 5-10 minutes
# Check data/processed/ directory
```

### Data collection is stuck

**Problem**: Data collection running but not progressing

**Solutions**:

1. **Check internet**
   ```bash
   ping google.com
   # Should get responses
   ```

2. **Try again**
   ```bash
   # Ctrl+C to cancel
   # Run again:
   python main.py --setup
   ```

3. **Skip Wikipedia** (faster alternative)
   ```bash
   # Edit src/data_collector.py
   # Comment out: wiki_data = self.collect_wikipedia_content(...)
   # Save and run: python main.py --setup
   ```

4. **Check disk space**
   ```bash
   df -h  # Mac/Linux
   # Need ~500MB free
   ```

### Incomplete data files

**Problem**: `data/processed/` is empty or incomplete

**Solutions**:

1. **Delete old files and restart**
   ```bash
   rm -rf data/raw/*
   rm -rf data/processed/*
   python main.py --setup
   ```

2. **Check file permissions**
   ```bash
   ls -la data/
   # Should have write permissions
   ```

3. **Manual check**
   ```bash
   python -c "
   import json
   with open('data/processed/feynman_processed_chunks.json') as f:
       data = json.load(f)
       print(f'Chunks: {len(data)}')
   "
   ```

---

## Performance Issues

### Responses are very slow

**Slow first response (30-60 seconds)?**
- This is normal - building vector index first time
- Subsequent responses are fast (1-5 seconds)

**All responses slow (>10 seconds)?**

**Solutions**:

1. **Check internet connection**
   ```bash
   ping -c 1 google.com  # Mac/Linux
   ping google.com       # Windows
   ```

2. **Check API status**
   - May be experiencing outages
   - Try `python main.py --query "test"`
   - Check https://status.cloud.google.com

3. **Reduce query complexity**
   ```bash
   # Instead of: "Write a 1000-word essay on quantum mechanics"
   # Use: "Explain quantum mechanics"
   ```

4. **Check disk speed**
   - If embeddings on slow drive, copy to SSD
   - Or adjust CHUNK_SIZE in config.py

### Memory usage is high

**Problem**: System using lots of RAM

**Solutions**:

1. **Close other applications**
   - Embeddings load into memory
   - Need ~500MB RAM

2. **Reduce embeddings**
   ```bash
   # Edit src/data_collector.py
   # Reduce max_results: 10 instead of 50
   # Collect fewer Wikipedia pages
   python main.py --setup  # Run again
   ```

3. **Check process**
   ```bash
   # Mac/Linux:
   top  # Shows memory usage
   # Windows:
   tasklist  # Shows processes
   ```

---

## Memory Issues

### "Session not saving"

**Problem**: Memory files not created

**Solutions**:

1. **Check memory directory**
   ```bash
   ls -la memory/
   # Should have write permissions
   ```

2. **Fix permissions**
   ```bash
   chmod -R 755 memory/  # Mac/Linux
   # Windows: Right-click folder → Properties → Security
   ```

3. **Check disk space**
   ```bash
   df -h  # Mac/Linux
   # Need space for JSON files (~1MB per session)
   ```

4. **Verify file creation**
   ```bash
   python -c "
   from pathlib import Path
   p = Path('memory')
   print(f'Memory dir exists: {p.exists()}')
   print(f'Is writable: {os.access(p, os.W_OK)}')
   "
   ```

### "Persistent memory corrupted"

**Problem**: Can't load persistent_memory.json

**Solution**:

```bash
# Backup old file
cp memory/persistent_memory.json memory/persistent_memory.json.bak

# Delete it (will be recreated)
rm memory/persistent_memory.json

# Run again - new file will be created
python main.py
```

---

## Runtime Errors

### "AttributeError" or "TypeError"

**Problem**: Code execution error

**Solutions**:

1. **Check Python version**
   ```bash
   python --version
   # Need 3.8+
   ```

2. **Reinstall dependencies**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. **Clear cache**
   ```bash
   find . -type d -name __pycache__ -exec rm -rf {} +
   find . -type f -name "*.pyc" -delete
   python main.py
   ```

4. **Restart Python**
   ```bash
   # Exit terminal completely
   # Reopen terminal
   cd feynman_twin/src
   python main.py
   ```

### "Out of Memory"

**Problem**: Not enough RAM

**Solutions**:

1. **Close other apps**
   - Browser, IDE, etc.
   - Need ~500MB free

2. **Reduce data**
   ```bash
   # Edit src/data_collector.py
   # Reduce numbers:
   # max_results=10  # instead of 50
   # fewer wikipedia_pages
   python main.py --setup
   ```

3. **Use lightweight mode**
   ```bash
   # Skip embeddings, use RAG-light
   # Edit src/main.py to disable RAG
   ```

### Connection timeout

**Problem**: Can't reach API

**Solutions**:

1. **Check internet**
   ```bash
   ping 8.8.8.8
   ```

2. **Check firewall**
   - May be blocking Python
   - Add Python to firewall whitelist

3. **Use VPN** (if needed)
   - If in region with restrictions
   - Connect to VPN first

4. **Try later**
   - May be temporary outage
   - Wait 5-10 minutes and retry

---

## Windows-Specific Issues

### batch file doesn't work

**Problem**: run.bat or quickstart.bat won't execute

**Solutions**:

1. **Try Python directly**
   ```batch
   python setup.py setup
   cd src
   python main.py
   ```

2. **Check batch syntax**
   ```bash
   # Edit run.bat or quickstart.bat
   # Make sure line endings are CRLF (not LF)
   # In VS Code: Bottom right → select CRLF
   ```

3. **Run as Administrator**
   - Right-click .bat file
   - "Run as Administrator"

### "is not recognized"

**Problem**: Python not found on Windows

**Solutions**:

1. **Add Python to PATH**
   - Control Panel → System → Environment Variables
   - Add Python installation folder to PATH
   - Restart terminal

2. **Use full path**
   ```batch
   C:\Python39\python.exe main.py
   ```

3. **Use py.exe launcher**
   ```batch
   py -3 main.py
   ```

---

## Mac-Specific Issues

### "Permission denied" on setup

**Solutions**:

```bash
# Make executable
chmod +x setup.py

# Or run with python directly
python setup.py setup
```

### Homebrew Python issues

**Solutions**:

```bash
# Use python3 explicitly
python3 --version
python3 setup.py setup
cd src
python3 main.py
```

---

## Linux-Specific Issues

### Missing dependencies

**Solutions**:

```bash
# Ubuntu/Debian
sudo apt-get install python3-pip python3-venv

# Fedora
sudo dnf install python3-pip python3-venv

# Then install project dependencies
pip install -r requirements.txt
```

---

## General Debugging

### Enable verbose output

```bash
# Set debug environment variable
export DEBUG=1  # Mac/Linux
set DEBUG=1     # Windows

python main.py --query "test"
```

### Check logs

```bash
# Logs are printed to console
# Save to file:
python main.py > output.log 2>&1

# View logs:
cat output.log  # Mac/Linux
type output.log # Windows
```

### Get system info

```bash
# For bug reports
python -c "
import sys
import platform
print(f'Python: {sys.version}')
print(f'OS: {platform.system()}')
print(f'Machine: {platform.machine()}')
"
```

---

## Still Having Issues?

### Step-by-step reset

1. **Backup your data**
   ```bash
   cp -r memory/ memory_backup/
   ```

2. **Clean installation**
   ```bash
   rm -rf embeddings/*
   rm -rf data/processed/*
   pip uninstall -r requirements.txt -y
   pip install -r requirements.txt
   ```

3. **Run setup again**
   ```bash
   python setup.py setup
   cd src
   python main.py --setup
   ```

### Get help

- Check [README.md](README.md#troubleshooting)
- Read [GETTING_STARTED.md](GETTING_STARTED.md)
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- Review [ARCHITECTURE.md](ARCHITECTURE.md)

### Report bugs

Include:
- Python version: `python --version`
- OS: Windows/Mac/Linux
- Error message (full)
- Steps to reproduce
- Relevant logs

---

## 🎓 Prevention Tips

1. **Keep .env safe** - backup before experimenting
2. **Save sessions** - type `memory` to confirm saving
3. **Check disk space** - need ~500MB
4. **Keep internet on** - needed for API calls
5. **Update regularly** - pip install --upgrade

---

**Most issues are:**
- ✓ API key configuration (check .env)
- ✓ Dependencies missing (run pip install)
- ✓ Data not collected (run main.py --setup)
- ✓ Slow first response (normal, expected)

**Still stuck?** Try the complete reset above, then the quick start guide again!
