import requests

response = requests.get('http://127.0.0.1:8000/games/editor-guest/', timeout=10)
print(f"Status: {response.status_code}")
print(f"URL: {response.url}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"First 500 chars:\n{response.text[:500]}")
print(f"\nSearching for key elements...")
print(f"  - blocklyDiv: {'blocklyDiv' in response.text}")
print(f"  - editor_enhanced: {'editor_enhanced' in response.text}")
print(f"  - Blockly: {'Blockly' in response.text}")
