# 🤖 Jarvis - Intelligent Voice Assistant

<div align="center">

**An advanced Python-based voice assistant with offline AI capabilities using Ollama**

Created by **Ahmed Qureshi**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)

</div>

---

## 📋 Table of Contents

- [About](#about)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

---

## About

**Jarvis** is an intelligent voice assistant built with Python that combines multiple AI backends to provide a seamless, fully offline experience. It can answer questions, control your computer, search the web, and perform various tasks using your voice.

### Key Highlights

✅ **Fully Offline** — Uses Ollama for local language models with zero internet dependency  
✅ **Smart Fallback System** — OpenAI GPT → Ollama LLM → Rule-Based QA → Document Search  
✅ **Zero API Costs** — Run your own models locally, no OpenAI API fees  
✅ **Cross-Platform** — Works on Windows, macOS, and Linux  
✅ **Voice-Enabled** — Speech recognition and text-to-speech capabilities  

---

## Features

### 🎯 Core Capabilities

- **Voice Recognition** — Understand and process voice commands
- **Text-to-Speech** — Speak responses naturally
- **AI-Powered Responses** — Multiple AI backends for intelligent answers
- **Web Search** — Search Wikipedia and the web for information
- **System Control** — Manage computer brightness, speed, and settings
- **Media Control** — Play music and videos
- **Translations** — Translate text between languages
- **Entertainment** — Tell jokes and more
- **Document Analysis** — Process and search PDF documents
- **Multi-Language Support** — Global communication

### 🔧 Technical Features

- **Hybrid AI System** — Combines rule-based QA, LLMs, and web search
- **Local Models** — Run Mistral, LLaMA, Neural Chat locally via Ollama
- **Graceful Degradation** — Works even when some backends are unavailable
- **Low Resource Usage** — Efficient processing with intelligent caching
- **Extensible Architecture** — Easy to add new features and integrations

---

## System Requirements

### Minimum Requirements

- **OS**: Windows 10+, macOS 10.12+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB (8GB+ recommended for Ollama)
- **Disk Space**: 5GB minimum (more for Ollama models)
- **Microphone**: For voice input
- **Speaker**: For voice output

### Optional Requirements

- **Ollama**: For offline AI capabilities (5-15GB depending on models)
- **OpenAI API Key**: For ChatGPT integration (optional, not required)

---

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ollama (Optional but Recommended)

**Windows:**
1. Download from [ollama.ai](https://ollama.ai)
2. Run the installer
3. Restart your computer

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### 3. Download an AI Model

Open PowerShell (Windows) or Terminal (Mac/Linux):

```bash
ollama pull mistral
```

### 4. Run Jarvis

**Windows:**
```bash
python jarvis.py
```

**macOS/Linux:**
```bash
python3 jarvis.py
```

### 5. Start Using Commands

Say things like:
- "What is machine learning?"
- "Tell me a joke"
- "Set brightness to 50%"
- "What's the weather like?"

---

## Installation

### Method 1: Manual Installation (Recommended)

#### Step 1: Clone or Download Repository
```bash
git clone https://github.com/yourusername/Python-Voice-Assistant.git
cd Python-Voice-Assistant
```

#### Step 2: Create Virtual Environment (Optional but Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Method 2: Automated Script Installation

**Windows:**
```bash
cd /path/to/Python-Voice-Assistant
.\Setup.bat
```

**Unix-based/Linux:**
```bash
cd /path/to/Python-Voice-Assistant
chmod +x Setup.sh
./Setup.sh
```

### Method 3: Running Jarvis Directly

**Windows:**
```bash
.\RUN_JARVIS.bat
```

Or with PowerShell:
```bash
.\RUN_JARVIS.ps1
```

**macOS/Linux:**
```bash
chmod +x RUN_JARVIS.sh
./RUN_JARVIS.sh
```

---

## Configuration

### 1. OpenAI API Key (Optional)

To use ChatGPT as a backend:

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign up and create an API key
3. In `jarvis.py`, find the line:
   ```python
   openai.api_key = "your-api-key-here"
   ```
4. Replace with your actual API key

### 2. Ollama Configuration

Ollama runs on `http://localhost:11434` by default. To use different models:

**Available Models:**
```bash
ollama pull mistral        # Recommended (7B, balanced)
ollama pull neural-chat    # Lightweight
ollama pull llama2         # Larger (13B)
ollama pull dolphin-mixtral # High performance
```

**Start Ollama Service:**

**Windows:**
```powershell
.\RESTART_OLLAMA.ps1
```

Or manually:
```powershell
ollama serve
```

### 3. Environment Variables

Create a `.env` file (optional):
```env
OPENAI_API_KEY=your-key-here
OLLAMA_HOST=http://localhost:11434
```

---

## Usage

### Starting Jarvis

```bash
python jarvis.py
```

The assistant will start listening and respond to voice commands.

### Basic Commands

**Information & Learning:**
- "What is Python?"
- "Tell me about machine learning"
- "Who is Elon Musk?"

**Entertainment:**
- "Tell me a joke"
- "Play a video on Python"
- "Translate 'Hello' to Spanish"

**System Control:**
- "Set brightness to 50%"
- "Check internet speed"
- "What time is it?"

**Web Operations:**
- "Search Wikipedia for quantum computing"
- "Open YouTube"
- "Send an email" (if configured)

### Advanced Usage

#### Running with Specific Models
Modify the model selection in `jarvis.py`:
```python
answer_with_ollama(query, model="mistral")
```

#### Custom Commands
Add your own commands in the `answer_with_offline_model()` function.

#### Batch Processing
For multiple commands without voice:
```python
python compile_test.py
```

---

## Troubleshooting

### Ollama Not Connecting

**Problem:** "Connection refused on localhost:11434"

**Solution:**
```powershell
# Windows - Restart Ollama
.\RESTART_OLLAMA.ps1

# Or manually
ollama serve
```

Check status:
```bash
python check_ollama.py
```

### Speech Recognition Issues

**Problem:** Microphone not detected

**Solution:**
- Check microphone permissions (Windows: Settings → Privacy → Microphone)
- Test microphone: `python test_import.py`
- Ensure no other app is using the microphone

### OpenAI API Errors

**Problem:** "API key invalid" or "Rate limit exceeded"

**Solution:**
- Verify API key at [OpenAI Dashboard](https://platform.openai.com/account/api-keys)
- Check account credits: [OpenAI Billing](https://platform.openai.com/account/billing/overview)
- Use Ollama as fallback (no API needed)

### Model Download Issues

**Problem:** Slow or failed downloads from Ollama

**Solution:**
```bash
# Check internet connection
ollama pull mistral --insecure

# Use a smaller model
ollama pull neural-chat  # ~4GB

# Clear cache
del %USERPROFILE%\.ollama\models  # Windows
rm -rf ~/.ollama/models            # macOS/Linux
```

**For more troubleshooting, see:**
- [OLLAMA_TROUBLESHOOTING.md](OLLAMA_TROUBLESHOOTING.md)
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md)
- [JARVIS_GUIDE.md](JARVIS_GUIDE.md)

---

## Architecture

### AI Fallback Chain

Jarvis uses an intelligent fallback system:

```
Voice Input
    ↓
Rule-Based QA (80+ cached answers)
    ↓ (if no match)
OpenAI ChatGPT (if API key available)
    ↓ (if fails or no key)
Ollama LLM (if service running)
    ↓ (if unavailable)
Local Document Search
    ↓ (if no docs match)
Friendly Response ("I don't have that info...")
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `jarvis.py` | Main voice assistant application |
| `requirements.txt` | Python dependencies |
| `Setup.bat/sh` | Automated installation scripts |
| `check_ollama.py` | Verify Ollama connectivity |
| `diagnose_ollama.py` | Troubleshoot Ollama issues |
| `ARCHITECTURE.md` | Detailed technical documentation |

### Technology Stack

- **Voice**: SpeechRecognition, pyttsx3
- **AI**: OpenAI GPT, Ollama (local models)
- **Web**: requests, BeautifulSoup4
- **System**: psutil, PyAutoGUI, WMI
- **Language**: Python 3.8+

---

## Contributing

We welcome contributions! To get started:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages:
   ```bash
   git commit -s -m "Add feature: description"
   ```
6. **Push** to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 code style
- Add comments for complex logic
- Test on Windows, macOS, and Linux if possible
- Update documentation for new features
- Keep dependencies minimal

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You are free to:
- Use this project for personal or commercial purposes
- Modify the code
- Distribute the code
- Use it privately

As long as you include the original license and copyright notice.

---

## Credits

**Created by:** Ahmed Qureshi

### Acknowledgments

This project builds upon:
- OpenAI's GPT models
- Ollama and local LLM technology
- The Python community and open-source libraries
- Contributors and users who provide feedback

---

## Support & Contact

**Have questions?** Check our documentation:
- [QUICKSTART.md](QUICKSTART.md) — Get started in 5 minutes
- [ARCHITECTURE.md](ARCHITECTURE.md) — Understand the system
- [JARVIS_GUIDE.md](JARVIS_GUIDE.md) — Complete user guide
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md) — Ollama configuration

**Found a bug?** Please open an issue with:
- Steps to reproduce
- Expected vs actual behavior
- Your system information
- Relevant logs or error messages

---

## Roadmap

Future enhancements planned:
- [ ] Multi-language voice support
- [ ] Advanced scheduling and reminders
- [ ] Integration with smart home systems
- [ ] Mobile app companion
- [ ] GUI dashboard
- [ ] Custom skill marketplace
- [ ] Cloud sync for settings

---

<div align="center">

**⭐ If you find this helpful, please consider starring the repository!**

Made with ❤️ by Ahmed Qureshi

</div>
