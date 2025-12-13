# Lupi-fy Game Creation Platform — Quick Start Guide

## Overview
Lupi-fy is a **drag-and-drop 2D game creation platform**. Users can build games using visual blocks, save versions, submit for review, and earn money from published games.

---

## 🚀 Getting Started (For Users)

### 1. Access the Platform
- **Tutorial:** http://127.0.0.1:8000/games/tutorial/
- **Editor:** http://127.0.0.1:8000/games/editor/
- **Moderation Panel (Admin):** http://127.0.0.1:8000/games/moderation/

### 2. Create Your First Game
1. Click **"Open Editor"** from the tutorial.
2. **Name your game** in the title field (e.g., "Flappy Bird Clone").
3. **Drag blocks** from the left panel into the workspace:
   - **Events:** "On Start", "On Collision", "On Key Press"
   - **Actions:** "Move Sprite", "Change Health", "Destroy Sprite", "Spawn Sprite"
4. **Run Preview** to test your logic.
5. **Save** to store your game (as Draft).
6. **Publish** to submit for moderator review.

### 3. Submit for Review
Once you publish, a moderator will review your game and approve it for the public if it meets quality standards.

---

## 🛠️ Backend API Endpoints

### Authentication
- `POST /api/auth/register/` — Create a new account
- `POST /api/auth/token/` — Obtain JWT token
- `POST /api/auth/token/refresh/` — Refresh JWT token
- `GET /api/auth/me/` — Get current user info

### Games
- `POST /games/api/save/` — Save a game version
  ```json
  {
    "title": "My Game",
    "description": "A fun game",
    "logic_json": {"events": [...]},
    "bundle_url": "local://bundle",
    "visibility": "draft"
  }
  ```
- `POST /games/api/publish/?game_id=<id>` — Submit for review
- `GET /games/api/games-list/` — List all games (Moderator/Admin only)
- `POST /games/api/approve/?game_id=<id>` — Approve a game (Moderator/Admin only)
- `POST /games/api/reject/?game_id=<id>` — Reject a game (Moderator/Admin only)

---

## 👨‍💻 Development Setup

### Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Backend URL:** http://127.0.0.1:8000/

### Frontend (Optional React + Vite)
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## 📋 User Roles & Permissions

| Role | Create Games | Edit | Publish | Review/Approve | Monetize |
|------|--------------|------|---------|----------------|----------|
| **Player** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Developer** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Moderator** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🎮 Editor Features

### Block Types
1. **Events**
   - `On Start` — Triggered when game loads
   - `On Collision` — Triggered when two objects collide
   - `On Key Press` — Triggered when player presses a key

2. **Actions**
   - `Move Sprite` — Move an object (X, Y direction)
   - `Change Health` — Add/subtract health points
   - `Destroy Sprite` — Remove an object
   - `Spawn Sprite` — Create a new object at position

3. **Logic**
   - `If/Else` — Conditional statements
   - `Compare` — Equality/inequality checks

### Workflow
1. **Design:** Drag blocks to build game logic.
2. **Preview:** Click "Run Preview" to test.
3. **Save:** Click "Save" to store a version.
4. **Publish:** Click "Publish" to submit for review.
5. **Monitor:** Check status in moderation panel.

---

## 🔐 Admin Moderation Panel

**URL:** http://127.0.0.1:8000/games/moderation/

### Features
- **View Pending Games:** Games awaiting review
- **Approve/Reject:** Accept or send back games
- **View Stats:** Total games, pending count, approved count

### Test Moderation
1. Create an account with role **"developer"**.
2. Build and publish a game.
3. Switch to an **"admin"** or **"moderator"** account.
4. Visit the moderation panel.
5. Approve or reject the game.

---

## 📊 Database Models

### Game
```python
{
  "id": "uuid",
  "owner_id": "user_id",
  "title": "string",
  "description": "string",
  "visibility": "draft|pending|public|private",
  "tags": ["tag1", "tag2"],
  "monetization_enabled": false,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GameVersion
```python
{
  "game_id": "uuid",
  "version_number": 1,
  "bundle_url": "string",
  "logic_json": {"events": [...]},
  "is_published": false,
  "created_at": "datetime"
}
```

### Score
```python
{
  "game_id": "uuid",
  "player_id": "user_id",
  "value": 1234.5,
  "meta": {},
  "created_at": "datetime"
}
```

---

## 🎯 Example Game: Simple Dodge Game

### Blocks Used
1. **On Start**
   - Spawn "player" at X=200, Y=300
   - Spawn "enemy" at X=100, Y=50

2. **On Key Press** (arrow_left)
   - Move "player" X=-10

3. **On Key Press** (arrow_right)
   - Move "player" X=+10

4. **On Collision** (player, enemy)
   - Change "player" health by -10
   - Spawn "powerup" at X=400, Y=200

5. **On Key Press** (space)
   - If player health > 0
     - Destroy "enemy"

---

## 🚀 Next Steps (Future Development)

### Short Term
- [ ] Asset upload (sprites, backgrounds, sounds)
- [ ] Multiplayer synchronization (WebSockets)
- [ ] Leaderboards and scoring system
- [ ] In-game monetization (ads, premium content)

### Medium Term
- [ ] AI assistant for game improvement suggestions
- [ ] Advanced physics engine
- [ ] Game analytics dashboard
- [ ] Marketplace for assets

### Long Term
- [ ] 3D game support
- [ ] Blockchain-based token system
- [ ] Creator community tools
- [ ] Export to standalone executables

---

## 🔗 Links & Resources

- **Main Site:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API Docs:** See endpoints above
- **GitHub:** [Your repo]

---

## 💬 Questions?

- Check the **Tutorial** at `/games/tutorial/`
- Report issues in the **Admin Panel**
- Contact support for help

Happy creating! 🎮✨
