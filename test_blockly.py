#!/usr/bin/env python3
import urllib.request
import time

time.sleep(2)

try:
    response = urllib.request.urlopen('http://localhost:8000/games/editor/', timeout=10)
    content = response.read().decode('utf-8')
    
    print("✅ Page loaded successfully")
    
    checks = {
        'blocklyDiv': 'id="blocklyDiv"' in content,
        'toolbox': 'id="toolbox"' in content,
        'Blockly CDN': 'blockly' in content.lower(),
        'initializeEditor': 'initializeEditor' in content,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")
        
except Exception as e:
    print(f"❌ Error: {e}")
