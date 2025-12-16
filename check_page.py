import urllib.request
import time

time.sleep(2)

try:
    response = urllib.request.urlopen('http://localhost:8000/games/editor-enhanced/', timeout=10)
    content = response.read().decode('utf-8')
    print("Content length: {}".format(len(content)))
    print("Contains LupiForge: {}".format('LupiForge' in content))
    print("Contains editor_enhanced: {}".format('editor_enhanced' in content))
    print("First 1000 chars:")
    print(content[:1000])
except Exception as e:
    print("Error: {}".format(e))
