# Ollama Setup Guide for Jarvis

This guide explains how to set up Ollama for offline LLM inference with Jarvis.

## What is Ollama?

Ollama is a tool to run large language models locally on your computer without needing OpenAI API or internet (after first setup). Models run on CPU (no GPU required, though GPU is faster).

## Installation Steps

### Windows

1. **Download Ollama**
   - Visit [ollama.ai](https://ollama.ai)
   - Download the Windows installer
   - Run the installer and follow prompts (will install Ollama service)

2. **Verify Installation**
   ```powershell
   ollama --version
   ```

3. **Download a Model** (first time only, ~5-10 minutes depending on model)
   ```powershell
   ollama pull mistral
   ```
   
   Other recommended models:
   ```powershell
   ollama pull neural-chat      # Smaller, faster (~4GB)
   ollama pull llama2           # Popular, conversational (~7GB)
   ollama pull dolphin-mixtral  # Good reasoning (~27GB)
   ```

4. **Start Ollama Service** (runs in background)
   ```powershell
   ollama serve
   ```
   
   Or if already running as a service, verify it's active:
   ```powershell
   # Open new PowerShell and test:
   curl http://localhost:11434/api/tags
   ```

## How Jarvis Uses Ollama

When you ask Jarvis a question:

1. **With OpenAI key**: Tries OpenAI first, then Ollama if OpenAI fails or is unavailable
2. **Without OpenAI key**: Tries Ollama directly, then falls back to rule-based answers

Example:
```powershell
# Without OpenAI key (forces Ollama)
$env:OPENAI_API_KEY=''

# In another terminal, ensure Ollama is running:
ollama serve

# In first terminal, run Jarvis:
.\.venv\Scripts\python.exe jarvis.py
```

## Quick Test

### Terminal 1: Start Ollama Service
```powershell
ollama serve
```

### Terminal 2: Test Jarvis
```powershell
$env:OPENAI_API_KEY=''
@'
what is machine learning
what is artificial intelligence
how does a transformer work
quit
'@ | .\.venv\Scripts\python.exe jarvis.py
```

## Troubleshooting

### "Connection refused" error
- Ollama is not running. Open a terminal and run: `ollama serve`
- Ensure port 11434 is not blocked by firewall

### "Unknown model" error
- Pull the model first: `ollama pull mistral`
- Jarvis tries models in this order: mistral → neural-chat → llama2 → dolphin-mixtral
- If none exist, falls back to rule-based answers

### Ollama responds slowly
- First inference is slower (model loads from disk)
- Subsequent questions are faster
- For faster responses, pull `neural-chat` (smaller model): `ollama pull neural-chat`

### Out of memory error
- Reduce model size or close other applications
- For limited RAM, use: `ollama pull neural-chat` or `ollama pull orca-mini`

## Model Recommendations

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **mistral** | ~4GB | Medium | High | Default, balanced |
| **neural-chat** | ~4GB | Fast | Good | Faster responses |
| **llama2** | ~7GB | Medium | High | Conversational |
| **dolphin-mixtral** | ~27GB | Slow | Excellent | Complex reasoning |
| **orca-mini** | ~1.7GB | Very Fast | Fair | Low-resource devices |

## Performance Tips

1. **First run is slow** — Ollama loads the model (~30s–2min depending on size). Subsequent calls are ~5–10s.
2. **Use smaller models on slow hardware** — Start with `neural-chat` or `orca-mini`.
3. **Dedicated GPU** — If you have NVIDIA GPU, Ollama automatically uses it for faster inference.
4. **Keep Ollama running** — Start `ollama serve` once; Jarvis connects to it continuously.

## Offline Workflow

1. Install Ollama + model (requires internet once)
2. Start `ollama serve` in background (no internet needed)
3. Run Jarvis — it will answer any question using Ollama model
4. No internet, no API key, no limits, no costs

---

**Questions answered by Jarvis offline:**
- AI/ML/DL concepts, computer science, software engineering, algorithms, data structures
- General knowledge (history, geography, science, medicine basics)
- Code examples, debugging help, technical explanations
- ...anything the language model knows!

Enjoy your offline smart AI assistant! 🚀
