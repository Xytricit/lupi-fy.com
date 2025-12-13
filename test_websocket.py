#!/usr/bin/env python
"""
Test WebSocket connection to game lobby
"""
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/game/lobby/"
    
    try:
        print(f"🔄 Attempting to connect to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Send a test message
            test_msg = {
                "action": "send_message",
                "message": "Test message"
            }
            print(f"📤 Sending: {test_msg}")
            await websocket.send(json.dumps(test_msg))
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 Received: {response}")
            
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
