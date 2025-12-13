# 🎮 LupiForge Editor - Quick Start Guide

## 🚀 Getting Started

1. **Open the Editor**
   - File: `templates/games/editor_enhanced.html`
   - Open in any modern browser
   - Console will show "✅ ALL SYSTEMS OPERATIONAL!"

2. **First Time Setup**
   - The editor loads with auto-generated project name "My Game"
   - Workspace has a starter block (on_game_start)
   - Change project name in the input field at top

---

## 📚 Main Features Overview

### 💾 Project Management (Top-Left)
- **Project Name**: Edit your game title (max 50 chars)
- **Save Button**: Save to localStorage
- **Export Code**: See generated JavaScript
- **Clear**: Clear workspace (requires confirmation)
- **Save Status**: Shows "Last saved: [time]"

### 🎮 Blockly Workspace (Center)
- **Drag & Drop Blocks**: Build game logic visually
- **8 Custom Blocks**:
  - Events: on_game_start, on_key_press, on_collision, on_timer
  - Actions: move_player, spawn_sprite, destroy_sprite, add_score
- **Standard Blocks**: Logic, Math, Variables

### 📦 Asset Manager (Right Sidebar)
- **Upload Button**: Add images/sounds
- **Tabs**: Sprites | Sounds | Backgrounds
- **Preview**: See uploaded assets
- **Delete**: Remove assets with confirmation
- **Collapse**: Toggle sidebar with ▼ button

### 🎮 Game Preview (Bottom Panel)
- **Play**: Run the game on canvas
- **Stop**: Pause execution
- **Restart**: Reset game
- **FPS Counter**: Performance monitor
- **Score Display**: Current game score

---

## 🏆 Header Features (Top-Right)

### Quick Access Buttons (Emoji Icons)
| Button | Feature | Purpose |
|--------|---------|---------|
| 🏆 | Leaderboard | Browse global high scores |
| 👥 | Social Hub | Follow creators, remix games |
| 📊 | Dashboard | View your game analytics |
| 🛡️ | Moderation | Review submitted games (Moderators) |
| 🎲 | Multiplayer | Create/join multiplayer rooms |
| ⚙️ | Settings | Configure preferences & profile |
| 🔔 | Notifications | View game status updates |

### Main Action Buttons
- **💾 Save**: Save current project
- **🚀 Publish**: Submit game to moderators
- **📤 Export**: Download generated code
- **🗑️ Clear**: Clear entire workspace

---

## 📊 Leaderboard 🏆

**Open**: Click 🏆 icon

**Features**:
- Filter by time period (Daily/Weekly/Monthly/All-Time)
- See your rank and best score
- View top players and their games
- Medals for top 3 (🥇🥈🥉)

---

## 👥 Social Hub

**Open**: Click 👥 icon

### Following Tab
- See creators you follow
- Unfollow with button
- Remix their games

### Followers Tab
- See who follows you
- View their profiles

### Discover Tab
- Search for creators
- View all users with stats
- Follow new creators
- **🎨 Remix**: Create copy of their game

---

## 📈 Creator Dashboard 📊

**Open**: Click 📊 icon

**View**:
- **Total Games**: Number of games created
- **Total Plays**: Total plays across all games
- **Followers**: Community size
- **Revenue**: Earnings from games

**Sections**:
- **Performance Chart**: Weekly plays visualization
- **Your Games**: Grid of all your games with stats
- **Revenue Breakdown**: Earnings per game

---

## 🛡️ Moderation Queue (Moderators Only)

**Access**: 
1. Click ⚙️ (Settings)
2. Go to Profile tab
3. Change Role to "Moderator"
4. Click 🛡️ icon (now visible)

**Features**:
- View pending games queue
- Quick approve ✅ / reject ❌
- Detailed review with game preview
- Add feedback for rejection
- Stats: Pending/Approved/Rejected today

---

## 🎲 Multiplayer Lobby

**Open**: Click 🎲 icon

### Browse Rooms Tab
- Search rooms by name
- Filter by game type
- Join available rooms
- See host, player count, ping

### Create Room Tab
- Enter room name
- Select game
- Set max players (2-8)
- Make private if desired
- Create and auto-join

### Active Sessions Tab
- See current multiplayer games
- Your active sessions with leave option

**In-Game HUD**:
- Fixed panel top-right during multiplayer
- Shows room name & player count
- Active player list with ping
- Leave room button

---

## ⚙️ Settings

**Open**: Click ⚙️ icon

### 👤 Profile Tab
- **Avatar**: Click to randomize emoji
- **Username**: Change your name
- **Bio**: Tell others about you
- **Role**: Select user role
  - Player (default)
  - Developer
  - Moderator (unlock moderation)
  - Admin

### 🎨 Preferences Tab
- **Theme**: Dark/Light/Auto
- **Animations**: Enable/disable UI animations
- **Notifications**: Toggle notification types
- **Auto-Save Interval**: 10/30/60 seconds
- **Snap to Grid**: Align blocks to grid

### 🔒 Privacy Tab
- **Profile Visibility**: Public/Friends/Private
- **Show Statistics**: Display game stats
- **Allow Messages**: Enable DMs
- **Show Online Status**: Display when online

### 🔑 Account Tab
- **Email**: Update account email
- **Password**: Change password (3 fields)
- **Danger Zone**: Delete account (irreversible)

---

## 🔔 Notifications

**Bell Icon**: 🔔 in top-right

**Features**:
- Unread count badge
- Dropdown list of notifications
- Mark individual as read
- Mark all as read
- Auto-clear read items
- Types: Game approved/rejected, followers, scores, etc.

---

## 💾 Save & Publish Workflow

### Saving
1. Edit project in Blockly
2. Click **💾 Save** OR auto-saves every 30 seconds
3. Status updates: "Last saved: Just now"
4. Saved to localStorage automatically

### Publishing
1. Click **🚀 Publish** button
2. Confirm game title
3. Modal shows publication details
4. Click **Publish Now**
5. Game queued for moderator review
6. Receive notification when approved/rejected

### Exporting
1. Click **📤 Export**
2. See generated JavaScript code
3. Copy for external use

---

## 🎮 Creating Games

### Step 1: Design Blocks
- Drag events (on_game_start, on_key_press)
- Add actions (move_player, spawn_sprite, add_score)
- Use logic/math for conditions

### Step 2: Upload Assets
- Click Asset Manager
- Upload sprites/backgrounds/sounds
- Drag into game preview

### Step 3: Test
- Click **Play** in preview
- Watch game run on canvas
- Check FPS counter

### Step 4: Save & Publish
- Save regularly (💾)
- When ready, publish (🚀)
- Monitor notifications for approval

---

## 📱 Data Persistence

### What Gets Saved
- ✅ Project blocks & configuration
- ✅ Uploaded assets (as data URLs)
- ✅ Achievement progress
- ✅ User settings & preferences
- ✅ Notification history
- ✅ Social connections

### Storage
- **Method**: Browser localStorage
- **Limit**: ~5-10MB per domain
- **Persistent**: Survives browser close
- **Reset**: Clear browser data to reset

---

## 🐛 Troubleshooting

### Moderation Button Not Showing
- Open Settings (⚙️)
- Go to Profile tab
- Change Role to "Moderator"
- Moderation button should appear

### Can't Find Uploaded Assets
- Check Asset Manager (right sidebar)
- Verify file type (images/audio only)
- Try uploading again

### Game Not Saving
- Check browser console (F12)
- Verify localStorage isn't full
- Try clearing other site data

### Performance Issues
- Disable animations in Settings
- Reduce FPS if too high
- Close unused modals

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+S | Save project |
| Ctrl+E | Export code |
| Ctrl+Z | Undo (Blockly) |
| Ctrl+Y | Redo (Blockly) |
| Delete | Remove selected block |

---

## 🎨 Tips & Tricks

### Block Organization
- Use comment blocks to group sections
- Color-code different block types
- Collapse category groups when not in use

### Asset Management
- Upload all assets upfront
- Use clear naming (player_sprite.png)
- Organize by type (sprites, sounds, etc.)

### Performance
- Check FPS during preview
- Limit concurrent sprites
- Use timers for delays

### Social Growth
- Build interesting games
- Follow other creators
- Ask for feedback
- Remix and improve

---

## 📞 Support

### Check Console
- Press F12 to open Developer Tools
- Go to Console tab
- Look for error messages

### Report Issues
- Note exact steps to reproduce
- Screenshot/describe error
- Check localStorage in DevTools

### API Documentation
- See comments in HTML source
- All API endpoints logged to console
- Backend integration guide in code

---

## 🎓 Learning Path

1. **Beginner**: Create simple on_game_start + move_player
2. **Intermediate**: Add collision detection, scoring
3. **Advanced**: Use timers, multiple sprites, conditions
4. **Expert**: Publish, optimize, build audience

---

## 🚀 Next Steps

1. ✅ Try creating a simple game
2. ✅ Save and export your code
3. ✅ Upload assets
4. ✅ Play in preview mode
5. ✅ Publish to moderators
6. ✅ Build your audience with social features
7. ✅ Track stats on dashboard

**Happy game building!** 🎮✨
