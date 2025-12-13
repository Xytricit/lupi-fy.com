import urllib.request
import sys
url = 'http://127.0.0.1:8000/games/editor-enhanced/'
try:
    with urllib.request.urlopen(url, timeout=5) as r:
        code = r.getcode()
        content = r.read().decode('utf-8', errors='replace')
        with open('response_editor_enhanced.html', 'w', encoding='utf-8') as f:
            f.write(content)
    print('OK', code)
except Exception as e:
    print('ERROR', e)
    sys.exit(2)
