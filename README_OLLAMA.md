# Jarvis — Smart Offline AI Voice Assistant

A Python-based voice assistant that works **fully offline** with local LLM (Ollama) and rule-based knowledge. Ask questions about **Computer Science, Software Engineering, AI/ML, and more** — get instant answers without OpenAI.

## Features

✅ **Offline-First** — Works without internet after setup  
✅ **Voice I/O** — Listen and speak via microphone/TTS  
✅ **Local LLM** — Powered by Ollama (Mistral, Llama2, etc.)  
✅ **Smart Fallback Chain** — OpenAI → Ollama LLM → Rule-based QA → Local docs search  
✅ **No Costs** — No API fees, no usage limits  
✅ **Comprehensive Knowledge** — AI, ML, CS, software engineering, finance, general QA  

## Quick Start

### 1. Install Ollama (One-Time Setup)

**Windows:**
- Download from [ollama.ai](https://ollama.ai)
- Run installer
- In PowerShell: `ollama pull mistral` (first model download ~4GB, one-time)

**macOS/Linux:**
```bash
curl https://ollama.ai/install.sh | sh
ollama pull mistral
```

### 2. Start Ollama Service

```powershell
# PowerShell (Windows)
ollama serve

# Or macOS/Linux
ollama serve
```

This runs in background on `localhost:11434`.

### 3. Run Jarvis

**Terminal 1** (already running Ollama):
```powershell
ollama serve
```

**Terminal 2**:
```powershell
cd "C:\Users\Humaira Kaleem\Desktop\Voice Assistant\Python-Voice-Assistant"
.\.venv\Scripts\python.exe jarvis.py
```

Or with microphone input disabled (for testing):
```powershell
# Set no API key to force offline + Ollama
$env:OPENAI_API_KEY=''

# Feed test queries
@'
what is machine learning
what is a transformer network
how does deep learning work
quit
'@ | .\.venv\Scripts\python.exe jarvis.py
```

## Offline Answer Workflow

Jarvis tries these in order:

1. **OpenAI GPT** (if `OPENAI_API_KEY` is set)
2. **Ollama LLM** (mistral → neural-chat → llama2 → dolphin-mixtral)
3. **Rule-Based QA** (pre-cached answers for 80+ topics)
4. **Local Docs Search** (README.md, Documentation/, *.txt)
5. **Friendly fallback** ("I don't have that info...")

## What Jarvis Can Answer Offline

**AI/ML/DL Topics:**
- What is machine learning? / What is artificial intelligence?
- Explain neural networks / transformers / attention / backpropagation
- Difference between supervised and unsupervised learning
- What is overfitting / underfitting / regularization?
- Transfer learning, embeddings, tokenization

**Computer Science:**
- Data structures, algorithms, complexity analysis
- Design patterns, OOP, functional programming
- Database fundamentals, SQL, NoSQL
- Networking, HTTP, REST APIs

**Software Engineering:**
- Version control (Git), CI/CD, DevOps
- Testing strategies, debugging
- System design, scalability

**Finance/Loans:**
- How to apply for a loan
- Understanding loan offers
- Credit scores, interest rates

**General Knowledge:**
- Time, date, jokes, weather (local APIs)
- Wikipedia lookup, web search
- Battery status, system info

...and **any question the Ollama LLM model knows!**

## Commands While Running

```
"time"               → Current time
"date"               → Current date
"help"               → List available commands
"weather"            → Weather (asks for city)
"news"               → Top headlines
"what is X"          → Ask any question
"open youtube"       → Open in browser
"search google"      → Search term
"quit" / "exit"      → Exit Jarvis
```

## Environment Variables (Optional)

```powershell
# Use OpenAI instead of Ollama (requires API key + internet)
$env:OPENAI_API_KEY='sk-...'
$env:OPENAI_MODEL='gpt-4o-mini'

# Or force offline-only (no OpenAI attempts)
$env:OPENAI_API_KEY=''
```

## Troubleshooting

**"Connection refused" when running Jarvis:**
- Ollama service not running. Open new terminal and run: `ollama serve`

**Model not found error:**
- Pull it: `ollama pull mistral`
- Or: `ollama pull neural-chat` (smaller, faster)

**Slow first response:**
- Normal — Ollama loads the model from disk (30s–2min first time)
- Subsequent responses are ~5–10s

**Out of memory:**
- Use smaller model: `ollama pull neural-chat` or `ollama pull orca-mini`
- Or close other applications

**Microphone not detected:**
- Check audio input settings
- Fallback to piped stdin for testing (see Quick Start above)

## File Structure

```
jarvis.py              ← Main assistant (voice loop + dispatcher)
OLLAMA_SETUP.md        ← Detailed Ollama setup guide
README.md              ← This file
requirements.txt       ← Python dependencies
Documentation/         ← Add your docs here (auto-indexed)
```

## Adding Custom Knowledge

Create Markdown/text files in `Documentation/`:

```markdown
## My AI Topics
- What is GANs? ...
- Attention mechanism deep dive ...
```

Jarvis will automatically search and return relevant snippets when asked.

## Offline Capabilities Summary

| Feature | Works Offline? | Requires |
|---------|---|---|
| Voice I/O | ✅ | Microphone + speakers |
| LLM QA | ✅ | Ollama + model |
| Rule-based QA | ✅ | None |
| Local doc search | ✅ | Docs in workspace |
| Weather | ❌ | Internet + API |
| News | ❌ | Internet + API |
| Wikipedia | ❌ | Internet |
| Web search | ❌ | Internet |
| OpenAI | ❌ | Internet + API key |

## Performance Notes

**CPU Usage:**
- Idle: ~5-10% (listening)
- Inference: ~50-100% (depends on model size)

**Memory:**
- Base: ~200MB
- With model loaded: ~2-8GB (depends on model)

**Response Time:**
- Mistral (4GB model): 5-10s per question
- Neural-chat (4GB): 3-5s per question
- Orca-mini (1.7GB): 2-3s per question

Use smaller models on low-resource systems.

## Future Enhancements

- [ ] Vector database + semantic search (FAISS)
- [ ] Multi-turn conversation memory
- [ ] Custom offline TTS voices
- [ ] Faster quantized models (GGUF)
- [ ] Web UI dashboard

## Contributing

Add more offline knowledge:
1. Create `.md` files in `Documentation/`
2. Add canned answers to `offline_knowledge` dict in `jarvis.py`
3. Test: `ollama serve` + query Jarvis

## License

MIT License — Use freely, modify as needed.

---

**Your complete offline AI assistant. No internet. No API keys. No monthly bills.** 🚀
