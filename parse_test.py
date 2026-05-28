import ast, traceback
try:
    with open('jarvis.py','r',encoding='utf-8') as f:
        src = f.read()
    ast.parse(src)
    print('OK')
except Exception:
    traceback.print_exc()
