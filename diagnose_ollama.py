#!/usr/bin/env python3
"""
Diagnostic script to check Ollama status and troubleshoot 500 errors.
Run this if you see "Ollama connection error: HTTP Error 500"
"""

import subprocess
import json
import urllib.request
import urllib.error
import time
import sys

print("=" * 70)
print("OLLAMA DIAGNOSTIC TOOL")
print("=" * 70)

# 1. Check if Ollama executable exists
print("\n[1] Checking Ollama executable...")
ollama_path = r"C:\Users\Humaira Kaleem\AppData\Local\Programs\Ollama\ollama.exe"
try:
    result = subprocess.run([ollama_path, "list"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"✓ Ollama executable found and working")
        print(f"  Output: {result.stdout[:200]}")
    else:
        print(f"✗ Ollama command failed: {result.stderr[:200]}")
except FileNotFoundError:
    print(f"✗ Ollama not found at {ollama_path}")
except Exception as e:
    print(f"✗ Error running Ollama: {e}")

# 2. Check if Ollama service is running
print("\n[2] Checking Ollama service...")
try:
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as response:
        data = json.loads(response.read().decode())
        models = data.get("models", [])
        print(f"✓ Ollama service is running")
        print(f"  Installed models: {len(models)}")
        for model in models:
            name = model.get("name", "unknown") if isinstance(model, dict) else model
            print(f"    - {name}")
except ConnectionRefusedError:
    print(f"✗ Ollama service not running. Start it with: ollama serve")
except Exception as e:
    print(f"✗ Error connecting to Ollama: {e}")

# 3. Test model inference
print("\n[3] Testing model inference...")
try:
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral:latest",
        "prompt": "Hello, what is your name?",
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode())
        if "response" in result:
            print("✓ Model inference working")
            print(f"  Response: {result['response'][:100]}...")
        else:
            print(f"✗ Unexpected response: {result}")
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}: {e.reason}")
    if e.code == 500:
        print("  → The model may still be loading, or there's a server issue")
        print("  → Try waiting 30 seconds and retrying")
        print("  → Or restart Ollama: killall ollama && ollama serve")
except Exception as e:
    print(f"✗ Inference error: {e}")

# 4. Check system resources
print("\n[4] Checking system resources...")
try:
    import psutil
    memory = psutil.virtual_memory()
    print(f"✓ System Memory:")
    print(f"  Available: {memory.available / (1024**3):.1f} GB")
    print(f"  Used: {memory.percent}%")
    if memory.available < 2 * 1024**3:
        print("  ⚠ WARNING: Less than 2GB available, Ollama may struggle")
except Exception as e:
    print(f"✗ Could not check system resources: {e}")

# 5. Recommendations
print("\n[5] Troubleshooting Recommendations:")
print("""
If you see "HTTP Error 500":
  1. The model might still be loading - wait 30 seconds
  2. Check available system memory (should be >2GB free)
  3. Restart Ollama:
     Open PowerShell and run:
       Stop-Process -Name "ollama" -Force
       & "C:\\Users\\Humaira Kaleem\\AppData\\Local\\Programs\\Ollama\\ollama.exe" serve
  4. Try a smaller model if RAM is limited:
       ollama pull neural-chat
     Then restart Jarvis

If Ollama is not running:
  1. Start Ollama in PowerShell:
     & "C:\\Users\\Humaira Kaleem\\AppData\\Local\\Programs\\Ollama\\ollama.exe" serve
  2. Keep this terminal open while using Jarvis
  3. Jarvis will work offline even if Ollama isn't responding

Quick Start:
  Terminal 1 - Start Ollama:
    & "C:\\Users\\Humaira Kaleem\\AppData\\Local\\Programs\\Ollama\\ollama.exe" serve
  
  Terminal 2 - Run Jarvis:
    cd "C:\\Users\\Humaira Kaleem\\Desktop\\Voice Assistant\\Python-Voice-Assistant"
    $env:OPENAI_API_KEY=''
    .\.venv\Scripts\python.exe jarvis.py
""")

print("\n" + "=" * 70)
