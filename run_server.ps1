#!/usr/bin/env pwsh
# Start the game server with WebSocket support using Daphne
.\.venv\Scripts\Activate.ps1
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
