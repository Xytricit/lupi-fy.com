#!/usr/bin/env python3

import urllib.request
import time
import re

time.sleep(2)

try:
    response = urllib.request.urlopen('http://localhost:8000/games/editor-enhanced/', timeout=10)
    content = response.read().decode('utf-8')
    
    print("[PASS] Page loaded successfully")
    print()
    
    checks = {
        'terminalPanel': 'id="terminalPanel"' in content,
        'terminalBtn': 'id="terminalBtn"' in content,
        'terminalInputField': 'id="terminalInputField"' in content,
        'terminalOutput': 'id="terminalOutput"' in content,
        'EnhancedTerminalManager': 'const EnhancedTerminalManager' in content,
        'safeInit method': 'safeInit()' in content,
        'DOMContentLoaded check': "document.readyState === 'loading'" in content,
    }
    
    print("Terminal Element Checks:")
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print("[{}] {}".format(status, check))
    
    print()
    
    checks_safe = {
        'Optional chaining in toggle': 'panel?.classList' in content,
        'Optional chaining in previewCode': 'this.editor?.value?.trim()' in content,
        'Null check in log': 'if (!output) return' in content,
        'Null check in attachEvents': 'if (terminalBtn)' in content,
    }
    
    print("Safety Fixes:")
    for check, result in checks_safe.items():
        status = "PASS" if result else "FAIL"
        print("[{}] {}".format(status, check))
    
    all_pass = all(checks.values()) and all(checks_safe.values())
    print()
    if all_pass:
        print("[SUCCESS] All terminal initialization fixes are in place!")
    else:
        print("[WARNING] Some checks failed. Please review the implementation.")
        
except Exception as e:
    print("[ERROR] {}".format(e))
