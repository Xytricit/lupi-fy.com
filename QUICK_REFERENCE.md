# 🎮 Lupi-fy Quick Reference - 30 Seconds to First Game

## ⚡ Start Here

### 1. **Launch Server**
```bash
cd "C:\Users\turbo\OneDrive\Documents\GitHub\lupi-fy.com"
python manage.py runserver
```
→ Server at: **http://localhost:8000**

### 2. **Create Your First Game**
- Go to: **http://localhost:8000/games/editor-enhanced/**
- Title your game
- Drag blocks from left → Workspace
- Click **Save** → **Publish**
- Done! ✅

---

## 🎮 Game Blocks Cheat Sheet

### Make Game Start
```
On Start → Spawn Sprite (player)
```

### Handle Input
```
On Key Press (Arrow Up) → Apply Velocity (player, 0, -400)
```

### Collision
```
On Collision (player, enemy) → Destroy Sprite (enemy)
```

### Score
```
Submit Score (1000) → Check Leaderboard
```

---

## 📊 Dashboard Quick Links

| What | Where |
|------|-------|
| **Create Game** | `/games/editor-enhanced/` |
| **My Stats** | `/games/dashboard/` |
| **Multiplayer** | `/games/multiplayer/` |
| **Leaderboard** | In editor, Leaderboard tab |
| **Revenue** | In dashboard, Revenue tab |
| **Moderation** (Admin) | `/games/moderation/` |

---

## 💡 Top 5 Features

1. **Block Editor** - Drag-drop game logic (no code!)
2. **Leaderboards** - Daily/Weekly/All-Time rankings
3. **Achievements** - Auto-unlock badges (>1000 score)
4. **Creator Dashboard** - See plays, revenue, stats
5. **Multiplayer** - Sessions, chat, player list

---

## 🔌 Most Used APIs

```javascript
// Save game
fetch('/games/api/save/', {
    method: 'POST',
    body: JSON.stringify({title, logic_json, visibility})
})

// Submit score
fetch('/games/api/submit-score/', {
    method: 'POST',
    body: JSON.stringify({game_id, score})
})

// Get leaderboard
fetch('/games/api/leaderboard/?game_id=X&period=weekly')

// Get AI suggestions
fetch('/games/api/ai/suggest-improvements/', {
    method: 'POST',
    body: JSON.stringify({logic_json})
})
```

---

## 🎯 Typical Game Creation Flow

```
1. Open Editor
   ↓
2. Add On Start Block
   ↓
3. Add Spawn Sprite Block
   ↓
4. Add On Key Press Block
   ↓
5. Add Move/Apply Velocity Block
   ↓
6. Save
   ↓
7. Publish (for review)
   ↓
8. Moderator Approves
   ↓
9. Game Goes Public
   ↓
10. Players Play & Score
    ↓
11. View Analytics in Dashboard
```

---

## 🛠️ Admin Commands

```bash
# Create superuser
python manage.py createsuperuser

# Database shell
python manage.py shell

# Reset migrations
python manage.py migrate games zero
python manage.py migrate accounts zero

# Check for issues
python manage.py check
```

---

## 📦 What's Included

✅ Game Editor (Blockly + Phaser)  
✅ 15+ Game Blocks  
✅ Asset Upload  
✅ Leaderboards  
✅ Achievements  
✅ AI Suggestions  
✅ Creator Dashboard  
✅ Multiplayer Lobby  
✅ Monetization  
✅ Moderation  
✅ User Profiles  
✅ 40+ APIs  

---

## ❓ FAQ

**Q: How do I make my game public?**  
A: Publish in editor → Moderator approves → Game goes public

**Q: Can I upload custom sprites?**  
A: Yes! Assets tab in editor-enhanced

**Q: How do achievements work?**  
A: Auto-unlock when score > 1000 (configurable)

**Q: Can I get paid for my game?**  
A: Yes! Enable monetization, track in Dashboard

**Q: Is multiplayer working?**  
A: UI ready, needs Django Channels setup for real-time

---

## 🚀 Quick Deploy Checklist

- [ ] Change `DEBUG = False` in settings.py
- [ ] Set up PostgreSQL database
- [ ] Configure S3 for media files
- [ ] Setup email backend
- [ ] Add Stripe/PayPal webhooks
- [ ] Enable HTTPS
- [ ] Setup monitoring
- [ ] Test all 40+ endpoints

---

## 📞 Key Files

| File | Purpose |
|------|---------|
| `games/models.py` | Game, Asset, Score models |
| `games/views.py` | Core game endpoints |
| `games/views_advanced.py` | Advanced features (AI, multiplayer, etc) |
| `templates/games/editor_enhanced.html` | Game editor UI |
| `templates/games/creator_dashboard.html` | Analytics dashboard |

---

## 🎓 Learning Resources

- **Block Docs:** See custom blocks in editor toolbar
- **API Docs:** See IMPLEMENTATION_COMPLETE_V2.md
- **Examples:** Check templates/games/*.html

---

**🎮 You're ready to build! Start at `/games/editor-enhanced/`**

*Made with ❤️ for creators*
