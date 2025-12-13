# Quick Start - Playing Games on lupi-fy.com

## Start the Server

Open PowerShell in the project directory and run:

```powershell
cd 'C:\Users\turbo\OneDrive\Documents\GitHub\lupi-fy.com'
.\.venv\Scripts\Activate.ps1
python manage.py runserver 8000
```

You'll see:
```
Starting development server at http://127.0.0.1:8000/
```

## Access the Games

### Try Not To Get Banned Game
Open in browser: http://127.0.0.1:8000/accounts/game/lobby/

**How to Play:**
1. Login with your account
2. See the 5-letter challenge
3. Chat with other players
4. Use challenge letters in your messages
5. Complete all letters = 20 points!
6. Watch out for banned words (60-second ban)

### Letter Set Game
Open in browser: http://127.0.0.1:8000/accounts/games/letter-set/

**How to Play:**
1. Login with your account
2. See the 7-letter set
3. Form words using those letters
4. Submit words for points
5. Track your completed words

## How It Works (Behind the Scenes)

### Game Architecture
- Games normally use WebSocket for real-time communication
- Django's `runserver` doesn't support WebSocket (expected behavior)
- **Fallback Solution:** Games automatically switch to HTTP polling
- Messages sent via regular HTTP POST requests
- Challenge data fetched via HTTP GET requests
- Slight latency (1-2 seconds) compared to production WebSocket

### What You'll See in Browser Console
```
⚠️ Switching to HTTP polling (runserver mode)
📡 Using polling mode (WebSocket unavailable)
✅ Challenge loaded! Letters: Y, O, C, P, H, N, ...
```

This is normal and expected - it means the fallback is working!

## Troubleshooting

### Games won't load
1. Check server is running: `Starting development server at http://127.0.0.1:8000/`
2. Make sure you're logged in
3. Check browser console for errors (F12)

### Messages not sending
1. Check internet connection
2. Server might have crashed - restart with `python manage.py runserver 8000`
3. Refresh the game page (F5)

### Ban system not working
- Bans automatically expire after 60 seconds
- Try using non-banned words
- Refresh page to see updated ban status

## Production Deployment

For production with native WebSocket support:

```bash
pip install daphne
daphne -b 0.0.0.0 -p 8000 mysite.asgi:application
```

Same game code runs unchanged, automatically uses WebSocket instead of polling.

## Testing

Run the test suite to verify everything works:

```bash
python test_game_functionality.py
```

Expected output:
```
SUCCESS: ALL TESTS PASSED
[OK] Game lobby loads successfully
[OK] Challenge endpoints working
[OK] Message endpoint supports both formats
Games are ready to play!
```

## Features

### Implemented & Tested ✅
- [x] Game page loading
- [x] Challenge letter generation
- [x] Message sending (via HTTP polling)
- [x] Challenge progress tracking
- [x] Ban system
- [x] Point system
- [x] New challenge generation
- [x] All endpoints responding correctly

### Known Limitations
- 1-2 second message latency (polling interval)
- Each client polls independently (no real-time broadcasting)
- Suitable for development, production uses native WebSocket

## Support Files

- **GAME_LOADING_FIX_SUMMARY.md** — Full technical details
- **GAME_POLLING_FALLBACK_GUIDE.md** — Architecture documentation
- **test_game_functionality.py** — Automated test suite

---

**Status:** Games operational and tested
**Server:** Ready at http://127.0.0.1:8000
**Last Updated:** December 12, 2025
