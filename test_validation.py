#!/usr/bin/env python
"""Validation tests for Lupi-fy platform."""

import urllib.request
import json

BASE_URL = 'http://127.0.0.1:8000'

print("\n" + "="*60)
print("BLOCKLY & PHASER VALIDATION")
print("="*60)

# Test 1: Blockly editor UI elements
r = urllib.request.urlopen(f'{BASE_URL}/games/editor-guest/')
html = r.read().decode('utf-8')

blockly_tests = {
    'Blockly injected': '<div id="blocklyDiv"' in html,
    'Toolbox present': '<xml id="toolbox"' in html,
    'Custom blocks (on_start)': 'on_start' in html,
    'Custom blocks (on_key_press)': 'on_key_press' in html,
    'Phaser canvas': 'phaser-container' in html,
    'Logic JSON textarea': '<textarea id="logic-json"' in html,
    'Save button': 'saveBtn' in html,
    'Export button': 'exportBtn' in html,
    'Publish button': 'publishBtn' in html,
    'Gravity toggle': 'gravityToggle' in html,
}

passed = 0
for test_name, result in blockly_tests.items():
    status = '✓' if result else '✗'
    print(f"{status} {test_name}")
    if result:
        passed += 1

print(f"\nBlockly/Phaser: {passed}/{len(blockly_tests)} PASS\n")

print("="*60)
print("API ENDPOINT VALIDATION")
print("="*60)

# Test 2: Key API endpoints
api_tests = [
    ('analyze-logic', 'POST', {'logic_json': {'events': []}}),
    ('leaderboard', 'GET', {}),
    ('achievements', 'GET', {}),
]

api_passed = 0
for endpoint, method, payload in api_tests:
    try:
        url = f'{BASE_URL}/games/api/{endpoint}/'
        req = urllib.request.Request(url, method=method)
        req.add_header('Content-Type', 'application/json')
        if method == 'POST':
            req.data = json.dumps(payload).encode('utf-8')
        r = urllib.request.urlopen(req)
        print(f"✓ /api/{endpoint}/ -> {r.getcode()}")
        api_passed += 1
    except Exception as e:
        error_msg = str(e)[:40]
        print(f"✗ /api/{endpoint}/ -> {error_msg}")

print(f"\nAPI Endpoints: {api_passed}/{len(api_tests)} PASS\n")

print("="*60)
print("DATABASE MODEL VALIDATION")
print("="*60)

# Test 3: Check models via Django ORM
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from games.models import Game, GameAsset, Score, Achievement, Transaction
from accounts.models import UserProfile, UserNotification, UserPreference

models = [
    ('Game', Game),
    ('GameAsset', GameAsset),
    ('Score', Score),
    ('Achievement', Achievement),
    ('Transaction', Transaction),
    ('UserProfile', UserProfile),
    ('UserNotification', UserNotification),
    ('UserPreference', UserPreference),
]

model_passed = 0
for name, model in models:
    try:
        count = model.objects.count()
        print(f"✓ {name} model exists ({count} records)")
        model_passed += 1
    except Exception as e:
        print(f"✗ {name} model -> {str(e)[:40]}")

print(f"\nDatabase Models: {model_passed}/{len(models)} PASS\n")

print("="*60)
print("SUMMARY")
print("="*60)
total_passed = passed + api_passed + model_passed
total_tests = len(blockly_tests) + len(api_tests) + len(models)
print(f"Overall: {total_passed}/{total_tests} tests PASS")
print(f"Status: {'✅ READY FOR DEPLOYMENT' if total_passed >= total_tests * 0.9 else '⚠️ NEEDS FIXES'}")
