import traceback
try:
    with open('jarvis.py','r',encoding='utf-8') as f:
        src = f.read()
    compile(src, 'jarvis.py', 'exec')
    print('OK')
except Exception:
    traceback.print_exc()
