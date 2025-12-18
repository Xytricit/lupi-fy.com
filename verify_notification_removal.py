#!/usr/bin/env python
import os

with open('templates/games/editor_enhanced.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

checks = {
    'NotificationManager': 'NotificationManager' not in content,
    'notificationBell': 'notificationBell' not in content,
    'notificationDropdown': 'notificationDropdown' not in content,
    'notification-bell CSS': '.notification-bell' not in content,
    'showToast function': 'showToast' in content,
}

print('NotificationManager Removal Verification:')
print('=' * 50)
for check, result in checks.items():
    status = 'PASS' if result else 'FAIL'
    print(f'[{status}] {check}: {result}')

all_pass = all(checks.values())
print('=' * 50)
print(f'Overall Status: {"PASS" if all_pass else "FAIL"}')
print()
if all_pass:
    print('✓ NotificationManager system successfully removed')
    print('✓ No DOM element references remaining')
    print('✓ showToast() fallback in place')
