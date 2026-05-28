#!/usr/bin/env python
"""Test RAG answer and verify it doesn't return wrong answers"""
import sys
sys.path.insert(0, '.')

# Mock speak to capture output
captured = []
def mock_speak(text):
    captured.append(text)
    print(f"[JARVIS]: {text[:150]}...")

# Set up environment
import os
os.environ['JARVIS_DEBUG'] = '1'

import jarvis
jarvis.speak = mock_speak

print("Testing RAG query fix:\n")
print("Q: what is RAG?")
jarvis.answer_with_offline_model("what is RAG?")

if captured:
    answer = captured[0]
    # Check if it's about RAG/retrieval or CODE_OF_CONDUCT
    if 'code of conduct' in answer.lower() or 'empathy' in answer.lower():
        print(f"\n❌ FAIL: Still getting CODE_OF_CONDUCT")
        print(f"Answer: {answer[:200]}")
    elif 'rag' in answer.lower() or 'retrieval' in answer.lower():
        print(f"\n✓ PASS: Got RAG answer!")
        print(f"Answer: {answer[:200]}")
    else:
        print(f"\n❓ Got different answer: {answer[:200]}")
else:
    print(f"\n❌ FAIL: No answer returned")
