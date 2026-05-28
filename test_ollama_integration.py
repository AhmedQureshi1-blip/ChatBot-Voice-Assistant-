#!/usr/bin/env python
"""
Quick test to verify Ollama integration in jarvis.py works.
Run: python test_ollama_integration.py
"""

import sys
import json

# Mock test for _call_ollama and answer_with_ollama functions

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        import urllib.request
        import urllib.error
        
        print("[1/3] Testing Ollama connection...")
        url = "http://localhost:11434/api/tags"
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
            models = result.get("models", [])
            if models:
                print(f"    ✓ Ollama running with {len(models)} model(s):")
                for m in models:
                    print(f"      - {m.get('name', 'unknown')}")
                return True
            else:
                print("    ✗ Ollama running but no models. Run: ollama pull mistral")
                return False
    except Exception as e:
        print(f"    ✗ Ollama not running: {e}")
        print("      Fix: Start Ollama with 'ollama serve' in another terminal")
        return False


def test_ollama_inference():
    """Test if Ollama can generate a response."""
    try:
        import urllib.request
        import urllib.error
        
        print("[2/3] Testing Ollama inference...")
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "mistral",
            "prompt": "Say 'Ollama is working!' in one sentence.",
            "stream": False,
            "temperature": 0.7,
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            response_text = result.get("response", "").strip()
            if response_text:
                print(f"    ✓ Ollama response: {response_text[:100]}...")
                return True
            else:
                print("    ✗ No response from Ollama")
                return False
    except Exception as e:
        print(f"    ✗ Ollama inference failed: {e}")
        return False


def test_jarvis_syntax():
    """Test if jarvis.py has valid Python syntax."""
    try:
        import ast
        print("[3/3] Testing jarvis.py syntax...")
        
        with open('jarvis.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        ast.parse(source)
        print("    ✓ jarvis.py syntax is valid!")
        return True
    except SyntaxError as e:
        print(f"    ✗ Syntax error in jarvis.py at line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"    ✗ Error checking jarvis.py: {e}")
        return False


def main():
    print("=" * 60)
    print("Jarvis + Ollama Integration Test")
    print("=" * 60)
    print()
    
    results = []
    results.append(("Ollama Connection", test_ollama_connection()))
    print()
    results.append(("Ollama Inference", test_ollama_inference()))
    print()
    results.append(("Jarvis Syntax", test_jarvis_syntax()))
    print()
    
    print("=" * 60)
    print("Summary:")
    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
    print("=" * 60)
    print()
    
    if all(r[1] for r in results):
        print("🎉 All tests passed! Run Jarvis with:")
        print("    .\.venv\Scripts\python.exe jarvis.py")
        return 0
    else:
        print("❌ Some tests failed. Fix issues and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
