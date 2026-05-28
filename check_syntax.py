#!/usr/bin/env python
import sys
import ast
import traceback

try:
    with open('jarvis.py', 'r', encoding='utf-8') as f:
        source = f.read()
    
    # Try to parse it
    ast.parse(source)
    print("✓ jarvis.py syntax is valid!")
    sys.exit(0)
except SyntaxError as e:
    print(f"✗ Syntax Error: {e}")
    print(f"  Line {e.lineno}: {e.text}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
