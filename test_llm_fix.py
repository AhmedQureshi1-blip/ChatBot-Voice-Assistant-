#!/usr/bin/env python
"""Test that LLM questions now return offline answers"""
import sys
import io
from contextlib import redirect_stdout

# Redirect speak output to capture instead of actual audio
sys.path.insert(0, '.')

# Temporarily replace speak function to capture output
captured_output = []
def mock_speak(text):
    captured_output.append(text)
    print(f"[JARVIS]: {text[:150]}...")

import jarvis
jarvis.speak = mock_speak

# Test queries
print("Testing LLM-related questions:\n")

test_cases = [
    "what is llm",
    "what is large language model",
    "what is llm in ai",
]

for query in test_cases:
    captured_output.clear()
    print(f"Q: {query}")
    try:
        jarvis.answer_with_offline_model(query)
        if captured_output:
            answer = captured_output[0]
            # Check if it's about CODE_OF_CONDUCT (bad) or LLM/language model (good)
            if 'code of conduct' in answer.lower() or 'demonstrating empathy' in answer.lower():
                print(f"  FAIL: Got CODE_OF_CONDUCT instead of LLM answer")
            elif 'llm' in answer.lower() or 'large language model' in answer.lower() or 'billion' in answer.lower():
                print(f"  PASS: Got LLM answer")
            else:
                print(f"  MAYBE: Got different answer: {answer[:80]}")
        else:
            print(f"  FAIL: No answer from offline KB")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()
