import requests

print("Testing Blockly Editor Fix (Debug Mode)...")
print("=" * 60)

try:
    response = requests.get('http://127.0.0.1:8000/games/editor-debug/', timeout=10)
    html = response.text
    
    checks = [
        ("HTML loads", response.status_code == 200),
        ("Contains blocklyDiv", 'id="blocklyDiv"' in html),
        ("Contains toolbox", 'id="toolbox"' in html),
        ("Contains on_game_start", "Blockly.Blocks['on_game_start']" in html),
        ("Contains on_key_press", "Blockly.Blocks['on_key_press']" in html),
        ("startApplication initialization", "All block definitions loaded" in html),
        ("Blockly CDN", 'blockly_compressed.min.js' in html),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("SUCCESS: All checks passed! Blockly is properly configured.")
    else:
        print("REVIEW: Some checks failed - see details above.")
    
    print(f"\nResponse size: {len(html)} bytes")
    print(f"Status code: {response.status_code}")
        
except Exception as e:
    print(f"ERROR: {e}")
