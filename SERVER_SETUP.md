# Game Server Setup

The game server requires Daphne ASGI server to support WebSockets for real-time multiplayer features.

## Quick Start

### Option 1: Use the PowerShell script (Recommended)
```powershell
.\run_server.ps1
```

### Option 2: Use the batch file (Windows)
```bash
run_server.bat
```

### Option 3: Manual command
```powershell
.\.venv\Scripts\Activate.ps1
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

## Access the Game
Once the server is running, visit:
- **Game Lobby**: http://localhost:8000/accounts/game/lobby/
- **Letter Set Game**: http://localhost:8000/accounts/games/letter-set/

## Server Status
When the server starts, you'll see:
```
2025-12-12 13:32:23,717 INFO     Listening on TCP address 0.0.0.0:8000
```

This means the server is ready! Use `Ctrl+C` to stop the server.

## Important Notes
- Make sure you're logged in before accessing games
- WebSocket connections will show in server logs as `WSCONNECT` 
- Debug messages show game interactions in real-time
