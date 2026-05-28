#!/usr/bin/env python
"""Direct test of Ollama API to diagnose the issue"""
import json
import urllib.request
import urllib.error

print("Testing Ollama API directly...\n")

# Test 1: Check if Ollama is running
print("1. Health check:")
try:
    with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2) as response:
        data = json.loads(response.read().decode())
        models = data.get("models", [])
        print(f"   ✓ Ollama is running")
        print(f"   ✓ Models installed: {[m.get('name') for m in models]}")
except Exception as e:
    print(f"   ✗ Ollama not responding: {e}")
    exit(1)

# Test 2: Direct API call with simple query
print("\n2. Testing direct Ollama API call with 'what is licensing in coding':")
query = "what is licensing in coding"
payload = {
    "model": "mistral:latest",
    "prompt": query,
    "stream": False,
    "temperature": 0.7,
    "num_predict": 180
}

try:
    req = urllib.request.Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode())
        answer = result.get("response", "").strip()
        if answer:
            print(f"   ✓ Got response from Ollama:")
            print(f"   Response: {answer[:200]}..." if len(answer) > 200 else f"   Response: {answer}")
        else:
            print(f"   ✗ Empty response from Ollama")
            print(f"   Full response: {result}")
except urllib.error.HTTPError as e:
    print(f"   ✗ HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check what jarvis.py's _call_ollama function returns
print("\n3. Testing jarvis.py _call_ollama function:")
try:
    from jarvis import _call_ollama
    answer = _call_ollama(query, model="mistral:latest", max_tokens=180)
    if answer:
        print(f"   ✓ _call_ollama returned:")
        print(f"   Answer: {answer[:200]}..." if len(answer) > 200 else f"   Answer: {answer}")
    else:
        print(f"   ✗ _call_ollama returned empty/None")
except Exception as e:
    print(f"   ✗ Error calling _call_ollama: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check answer_with_ollama
print("\n4. Testing jarvis.py answer_with_ollama function:")
try:
    import os
    os.environ['JARVIS_DEBUG'] = '1'
    
    # Mock speak to capture output
    captured = []
    import jarvis
    original_speak = jarvis.speak
    jarvis.speak = lambda x: captured.append(x)
    
    result = jarvis.answer_with_ollama(query)
    jarvis.speak = original_speak
    
    if result:
        print(f"   ✓ answer_with_ollama returned True")
        if captured:
            print(f"   ✓ Spoke: {captured[0][:200]}...")
    else:
        print(f"   ✗ answer_with_ollama returned False")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("SUMMARY: If step 2 works but step 3/4 fails, there's a bug in jarvis.py")
print("="*60)
