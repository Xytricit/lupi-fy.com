import requests

print("Testing Blockly Editor Fix...")
print("=" * 50)

try:
    response = requests.get('http://127.0.0.1:8000/games/editor-guest/', timeout=10)
    html = response.text
    
    checks = [
        ("HTML loads", response.status_code == 200),
        ("Contains blocklyDiv", 'id="blocklyDiv"' in html),
        ("Contains toolbox", 'id="toolbox"' in html),
        ("Contains on_game_start block", "Blockly.Blocks['on_game_start']" in html),
        ("Contains on_key_press block", "Blockly.Blocks['on_key_press']" in html),
        ("startApplication moved", "All block definitions loaded" in html),
        ("Blockly CDN linked", 'blockly_compressed.min.js' in html),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {check_name}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("SUCCESS: All checks passed! Blockly fix is working.")
    else:
        print("WARNING: Some checks failed.")
        
except Exception as e:
    print(f"ERROR: {e}")
