# Setting Up Your Gemini API Key

## Why Do You Need This?

The Feynman Digital Twin uses Google's Gemini API to:
- Generate intelligent responses
- Create vector embeddings for knowledge retrieval
- Fall back to alternative models if needed

Good news: **The free tier is more than enough!**

## Step-by-Step Setup

### Option 1: Google AI Studio (Easiest - Recommended)

**Step 1: Visit Google AI Studio**
1. Go to https://aistudio.google.com/app/apikeys
2. You may need to sign in with your Google account
3. Create a new account if you don't have one (free)

**Step 2: Create API Key**
1. Click the blue "Create API Key" button
2. Select "Create API key in new project"
3. Google will generate a key (looks like: `AIzaSy...`)

**Step 3: Copy Your Key**
1. Click the copy icon next to your key
2. The key is now in your clipboard

**Step 4: Add to .env File**
1. Open `feynman_twin/.env` in a text editor
2. Find the line: `GEMINI_API_KEY=your_api_key_here`
3. Replace `your_api_key_here` with your actual key
4. Save the file

**Step 5: Test It**
```bash
cd src
python main.py --query "Hello"
```

### Option 2: Google Cloud Console (Advanced)

If you prefer to use Google Cloud:

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable the Generative Language API
4. Create an API key under Credentials
5. Use the same steps as Option 1 for .env file

## Security Best Practices

⚠️ **IMPORTANT: Protect Your API Key!**

### DO:
- ✅ Keep `.env` file private (don't commit to git)
- ✅ Use `.gitignore` to prevent accidental sharing
- ✅ Keep key in local .env only
- ✅ Rotate key if accidentally exposed

### DON'T:
- ❌ Never share your API key
- ❌ Don't commit .env to version control
- ❌ Never paste key in public forums
- ❌ Don't use key in client-side code

### Create .gitignore

If tracking this in git, add to `.gitignore`:
```
.env
*.env
*.env.local
__pycache__/
*.pyc
embeddings/
memory/conversations/
data/raw/
data/processed/
```

## Verifying Your Setup

### Test Your API Key

```bash
python -c "import os; print('API Key:', os.getenv('GEMINI_API_KEY')[:10] + '...')"
```

Should output something like: `API Key: AIzaSy...`

### Test API Connection

```bash
cd src
python -c "
import google.generativeai as genai
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
print('✓ API Key Valid')
"
```

## Free Tier Limits

| Limit | Amount | Resets |
|-------|--------|--------|
| Requests | 60 per minute | Per minute |
| Queries | Unlimited* | Daily quota |
| Embeddings | Unlimited | Daily quota |
| Cost | $0 | Always free tier |

*Limited by quota, typically enough for hundreds of queries per day

## Upgrading (Optional)

### When to Consider Paid Plan

- Using more than 100 queries per day
- Heavy production use
- Enterprise needs

### Pricing

| Model | Input Cost | Output Cost |
|-------|-----------|-----------|
| Gemini 2.5 Flash | Free tier: unlimited | Free tier: unlimited |
| | Paid: $0.01/1M | $0.04/1M |
| Gemini 1.5 Pro | Free tier: $5/month | - |
| | Paid: $1.50/1M | $6/1M |

For typical use, free tier is sufficient.

## Troubleshooting

### "GEMINI_API_KEY not set"

**Problem**: System can't find your API key

**Solutions**:
1. Check `.env` file exists in `feynman_twin/` directory
2. Verify format: `GEMINI_API_KEY=AIzaSy...` (no quotes)
3. No spaces: `GEMINI_API_KEY=AIza...` (correct)
4. Bad: `GEMINI_API_KEY = AIza...` (extra spaces)
5. Restart terminal after editing `.env`

### "Invalid API key"

**Problem**: Key exists but doesn't work

**Solutions**:
1. Verify key copied completely (no missing characters)
2. Check key hasn't been regenerated (old key invalidated)
3. Ensure no extra spaces or line breaks
4. Generate a new key and try again

### "Quota exceeded"

**Problem**: Hit free tier limits

**Solutions**:
1. Wait for quota reset (typically hourly or daily)
2. Consider upgrading to paid tier
3. Reduce query frequency
4. Use batch processing during off-peak

### "Permission denied"

**Problem**: API enabled but permissions missing

**Solutions**:
1. Regenerate API key
2. Verify project has Generative Language API enabled
3. Try Google AI Studio instead of Cloud Console

## .env File Format

### Correct Format:
```
GEMINI_API_KEY=AIzaSyDummyKeyExample123456789
```

### Common Mistakes:

❌ Wrong: Extra spaces
```
GEMINI_API_KEY = AIzaSy...
```

❌ Wrong: Quotes around key
```
GEMINI_API_KEY="AIzaSy..."
```

❌ Wrong: Multiple assignments
```
GEMINI_API_KEY=AIzaSy...
GEMINI_API_KEY=AIzaSy...
```

✅ Right: Simple format
```
GEMINI_API_KEY=AIzaSyDummyKeyExample123456789
```

## Checking Current Setup

### On Windows:
```batch
set | findstr GEMINI
```

### On Mac/Linux:
```bash
echo $GEMINI_API_KEY
```

### In Python:
```python
import os
print(os.getenv("GEMINI_API_KEY"))
```

## Advanced: Environment Variables

If you prefer not to use .env file:

### Windows (Command Prompt):
```batch
setx GEMINI_API_KEY "your_key_here"
# Then restart terminal
```

### Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY = "your_key_here"
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_key_here", "User")
```

### Mac/Linux (Bash):
```bash
export GEMINI_API_KEY="your_key_here"
# Add to ~/.bashrc for persistence:
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## Rotating Keys (Security)

If you suspect your key was exposed:

1. Go to https://aistudio.google.com/app/apikeys
2. Delete the exposed key
3. Generate a new key
4. Update .env file
5. Restart application

Old key immediately becomes invalid.

## Multi-Key Setup (Advanced)

If running multiple instances:

```
.env.dev
.env.prod
.env.backup
```

Load conditionally:
```python
from dotenv import load_dotenv
import os

env = os.getenv("ENV", "dev")
load_dotenv(f".env.{env}")
```

## Monitoring Usage (Optional)

Track your API usage:

1. Visit https://console.cloud.google.com
2. Go to APIs & Services > Library
3. Search for "Generative Language API"
4. View quotas and usage

## Getting Help

If you encounter API issues:

1. Check [Gemini Documentation](https://ai.google.dev/docs)
2. Visit [Stack Overflow](https://stackoverflow.com/questions/tagged/google-generative-ai)
3. Check [GitHub Issues](https://github.com/google/generative-ai-python)

## Summary

```
1. Get key: https://aistudio.google.com/app/apikeys
2. Edit .env file with your key
3. Save and test
4. Start using Feynman Twin!
```

That's it! You're ready to go.

---

**Next Step**: Return to [GETTING_STARTED.md](GETTING_STARTED.md) to continue setup.
