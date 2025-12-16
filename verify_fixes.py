#!/usr/bin/env python3

with open('templates/games/editor_enhanced.html', 'r', encoding='utf-8') as f:
    content = f.read()

checks = {
    'safeInit method': 'safeInit()' in content,
    'DOMContentLoaded check': "document.readyState === 'loading'" in content,
    'Optional chaining panel': 'panel?.classList' in content,
    'Optional chaining editor': 'this.editor?.value?.trim()' in content,
    'Null check output': 'if (!output) return' in content,
    'Null check terminalBtn': 'if (terminalBtn)' in content,
}

print('Terminal Initialization Fixes Check:')
for check, result in checks.items():
    status = 'PASS' if result else 'FAIL'
    print('[{}] {}'.format(status, check))

all_pass = all(checks.values())
print()
if all_pass:
    print('[SUCCESS] All terminal fixes are in place!')
else:
    print('[ERROR] Some fixes are missing!')
