#!/usr/bin/env python3
"""
Quick Ollama Status Check
Shows if Ollama is running and which models are available
"""
import json
import sys

try:
    import urllib.request
    import urllib.error
    
    print("Checking Ollama status...")
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
            data = json.loads(response.read().decode())
            models = data.get("models", [])
            
            print("\n✓ Ollama is RUNNING")
            print(f"✓ {len(models)} model(s) installed:")
            for model in models:
                name = model.get("name", "unknown") if isinstance(model, dict) else model
                print(f"  - {name}")
            print("\n✓ Jarvis will use Ollama for answers")
            sys.exit(0)
    except ConnectionRefusedError:
        print("\n✗ Ollama is NOT running")
        print("\nTo start Ollama, open PowerShell and run:")
        print('  & "C:\\Users\\Humaira Kaleem\\AppData\\Local\\Programs\\Ollama\\ollama.exe" serve')
        print("\nKeep that terminal open. Jarvis will work offline until Ollama starts.")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\n✗ Cannot connect to Ollama: {e}")
        print("\nEnsure Ollama is running:")
        print('  & "C:\\Users\\Humaira Kaleem\\AppData\\Local\\Programs\\Ollama\\ollama.exe" serve')
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
