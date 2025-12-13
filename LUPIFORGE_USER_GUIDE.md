# 🎮 LupiForge: Complete Beginner's Guide to Mastering 2D Game Creation

**Welcome to LupiForge!** This guide will teach you everything you need to create, publish, and share amazing 2D games—even if you've never programmed before.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Planning Your Game](#planning-your-game)
4. [Using the AI Assistant](#using-the-ai-assistant)
5. [Step-by-Step Game Creation](#step-by-step-game-creation)
6. [Best Practices](#best-practices)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Summary & Next Steps](#summary--next-steps)
10. [Quick-Start Cheat Sheet](#quick-start-cheat-sheet)

---

## Introduction

### What is LupiForge?

**LupiForge** is a visual game creation platform that lets you build 2D games without writing code. Instead of typing code, you use a **drag-and-drop block editor** similar to Scratch or Blockly. You can create:

- 🎮 Action games with players and enemies
- 🏃 Platformers with jumping and obstacles
- 🎯 Puzzle games with timers and scoring
- 👾 Adventure games with multiple sprites
- 🏆 Multiplayer games with global leaderboards

### Key Features

| Feature | What It Does |
|---------|--------------|
| 🎨 **Blockly Editor** | Drag blocks to build game logic visually |
| 📦 **Asset Manager** | Upload and organize sprites, sounds, backgrounds |
| 🎮 **Live Preview** | Play your game instantly while building |
| 🏆 **Leaderboards** | Submit scores and see global rankings |
| 👥 **Social Hub** | Follow creators and remix their games |
| 📊 **Dashboard** | Track game plays and statistics |
| 🤖 **AI Assistant** | Get help with game ideas and strategy |
| 🎲 **Multiplayer** | Create games multiple players can enjoy together |

### Who This Guide Is For

- Beginners with **no programming experience**
- Students learning game design
- Educators teaching game creation
- Anyone wanting to create their first 2D game

---

## Getting Started

### Step 1: Access LupiForge

1. Open your web browser (Chrome, Firefox, Edge, or Safari)
2. Go to **https://lupi-fy.com**
3. Click **"Create New Game"** or **"Open Editor"**

### Step 2: Sign In / Create Account

- If you have an account, **log in** with your email and password
- If you're new, click **"Sign Up"** and fill in:
  - Your username (this is public)
  - Your email address
  - A password
  - Agree to terms and click **"Create Account"**

### Step 3: Understand the Editor Layout

When you open the editor, you'll see four main areas:

```
┌─────────────────────────────────────────────────────────────┐
│ 💾 Save  🚀 Publish  📤 Export  🗑️ Clear  [My Game]       │ ← Header
├────────────┬─────────────────────────────┬──────────────────┤
│   Tools    │   Blockly Workspace         │   Asset Manager  │
│            │   (Drag blocks here)        │   (Sprites/Sounds)│
│   Blocks   │                             │                  │
│            │                             │   Upload Button  │
├────────────┴─────────────────────────────┴──────────────────┤
│            Game Preview (Play area)                          │
│            [▶️ Play] [⏹️ Stop] [🔄 Restart]  FPS: 60      │
└─────────────────────────────────────────────────────────────┘
```

**The Four Areas:**

1. **Header (Top)**: Save, publish, and export your game
2. **Left Sidebar**: Available blocks to drag into your workspace
3. **Center Workspace**: Where you build your game by dragging blocks
4. **Right Sidebar**: Upload and manage your game assets
5. **Bottom Panel**: Preview area where your game runs

---

## Planning Your Game

### Before You Code: Ask Yourself These Questions

Before jumping into the editor, spend **5-10 minutes** planning:

#### 1. **What's the Core Idea?**
   - Write one sentence: "My game is about _________"
   - Example: "My game is about a spaceship avoiding asteroids"

#### 2. **What Will Players Do?**
   - **Main Action**: What's the primary thing players repeat?
     - Jump over obstacles?
     - Collect items?
     - Answer questions?
     - Avoid enemies?
   - Example: "Players control a spaceship and avoid asteroids"

#### 3. **What's the Goal?**
   - How do players win or achieve success?
     - Get the highest score?
     - Reach a destination?
     - Survive the longest?
   - Example: "Survive for 60 seconds to win"

#### 4. **What Game Elements Do You Need?**
   - **Sprites**: Player character, enemies, items, obstacles
   - **Controls**: Keyboard keys (arrow keys, WASD, space)
   - **Feedback**: Score, health, timers
   - **Audio** (optional): Sound effects, background music
   - Example: "Spaceship (player), asteroids (obstacles), stars (score)"

#### 5. **Difficulty Progression**
   - Does it get harder over time?
   - How do you want players to feel challenged?
   - Example: "Asteroids spawn faster every 10 seconds"

### Planning Template

Copy and fill this out:

```
GAME TITLE: ________________________
CORE IDEA: ________________________
MAIN ACTION: ________________________
WINNING CONDITION: ________________________
KEY SPRITES: 
  - Player: _______________
  - Enemy/Obstacle: _______________
  - Item/Collectible: _______________
CONTROLS: _______________
DIFFICULTY PROGRESSION: _______________
```

---

## Using the AI Assistant

### What Can the AI Assistant Do?

The AI Creator Assistant helps you with:

✅ **Game Ideas**: "Give me ideas for a space game"  
✅ **Strategy Tips**: "How should I design difficulty progression?"  
✅ **Explanations**: "What's a sprite collision?"  
✅ **Motivation**: "I'm stuck, can you encourage me?"  
✅ **Creator Stats**: "What should I focus on next?"  

### How to Access the AI Assistant

1. Look in the editor header (top-right area)
2. Click the **💬 Chat** or **🤖 AI Helper** icon
3. Or find the **Chat Button** in the dashboard

### Example Conversations with AI

#### Example 1: Getting Game Ideas

**You**: "Help me design a simple platformer game"

**AI**: "Great choice! Here's a simple platformer structure:
- **Player**: A character that can move left/right and jump
- **Obstacles**: Platforms at different heights and moving hazards
- **Goal**: Reach the top or collect 10 coins
- **Progression**: Add more platforms and tighter timing as difficulty increases

Start with these blocks: on_game_start, on_key_press, move_player, on_collision"

#### Example 2: Understanding Blocks

**You**: "What's the difference between on_collision and on_timer?"

**AI**: "Great question!
- **on_collision**: Triggers when two sprites touch (player hits enemy, collects item)
- **on_timer**: Triggers after X seconds (spawn enemy every 2 seconds, change difficulty every 30s)

For a platformer, use on_collision for coins and enemies, on_timer to spawn platforms"

#### Example 3: Asking for Motivation

**You**: "I'm frustrated, my game keeps crashing"

**AI**: "I feel you! Every creator hits this. Crashes usually mean:
1. Block logic conflict - check your conditions
2. Missing assets - upload your sprites first
3. Infinite loops - make sure timers have delays

Try simplifying to 3-4 blocks, test, then add more. You've got this! 💪"

### Tips for Getting Better AI Responses

| Do This | Avoid This |
|---------|-----------|
| Be specific: "How do I make a player jump?" | Vague: "How do I make a game?" |
| Describe your problem: "Collision not detecting" | Unclear: "It doesn't work" |
| Ask for examples: "Show me block examples" | Asking for full game code |
| Use creator language: "sprites", "collision" | Game jargon you don't understand |

---

## Step-by-Step Game Creation

### Phase 1: Set Up Your Project

#### Step 1.1: Create a New Game
1. Click **"New Game"** or start in the editor
2. Enter a **Project Name**: Something descriptive like "Asteroid Dodger"
3. Click **Save** (or it autosaves)
4. **Status**: You're in the editor, ready to build!

#### Step 1.2: Understand the Starting Blocks
You'll see a starter block: `on_game_start`

```
This is your first block - it runs ONCE when the game starts.
Think of it like "setup" in real life:
  - Set initial score to 0
  - Create the player
  - Start background music
```

---

### Phase 2: Create Your Player

#### Step 2.1: Upload Player Sprite
1. Click **Upload** in the right sidebar (Asset Manager)
2. Choose a **Sprites** tab
3. Select an image file (PNG recommended, transparent background)
4. Click **"Upload Sprite"**
5. **Example**: Use a simple circle, square, or character image

#### Step 2.2: Add Player Spawn Block
In the **Blockly Workspace**:
1. From the left sidebar, drag the **`spawn_sprite`** block into `on_game_start`
2. Configure it:
   - **Name**: "player" (must be lowercase, no spaces)
   - **Image**: Select your uploaded sprite
   - **X Position**: 200 (center horizontal)
   - **Y Position**: 400 (lower part of screen)
   - **Size**: 50 (pixels, adjust as needed)

```
Your block should look like:
┌─────────────────────────────────┐
│ on_game_start                   │
│  spawn_sprite                   │
│    name: "player"               │
│    image: [Your sprite]         │
│    at x: 200  y: 400            │
│    size: 50                     │
└─────────────────────────────────┘
```

---

### Phase 3: Add Player Controls

#### Step 3.1: Make Player Move Left/Right
1. Drag `on_key_press` block below `spawn_sprite`
2. Configure:
   - **Key**: Arrow Left ( ← )
3. Inside it, drag `move_player` block
4. Configure:
   - **Sprite**: "player"
   - **Direction**: Left
   - **Distance**: 15 (pixels per press)

Repeat for Arrow Right (→) with Direction: Right

```
Result:
┌──────────────────────────────────┐
│ on_key_press [←]                 │
│  move_player                     │
│    sprite: "player"              │
│    direction: left               │
│    distance: 15                  │
└──────────────────────────────────┘
```

#### Step 3.2: Add Jumping (Optional Advanced)
For jumping, use a **timer** to simulate gravity:
1. Add `on_timer` block (set to 50ms)
2. Move player DOWN when airborne
3. Use variables to track if player is in air

---

### Phase 4: Add Game Obstacles/Enemies

#### Step 4.1: Create Obstacles
1. Upload obstacle sprite (asteroid, enemy, etc.)
2. Use `on_timer` block (every 2 seconds):
   ```
   on_timer [2000 ms]
    spawn_sprite
      name: "obstacle_" + [random number]
      image: [obstacle sprite]
      at x: [random 0-500]  y: 0
      size: 40
   ```

#### Step 4.2: Make Obstacles Move
1. Use another `on_timer` (faster, like 100ms):
   ```
   on_timer [100 ms]
    move_player
      sprite: "obstacle"
      direction: down
      distance: 5
   ```

#### Step 4.3: Remove Off-Screen Obstacles
1. Use `destroy_sprite` block in condition:
   ```
   on_timer [100 ms]
    if sprite y > 600
      destroy_sprite "obstacle"
   ```

---

### Phase 5: Add Collision Detection & Game Logic

#### Step 5.1: Detect Collisions
1. Drag `on_collision` block
2. Configure:
   - **Sprite 1**: "player"
   - **Sprite 2**: "obstacle"
3. Inside it, add response (choose one):
   - **Player dies**: `destroy_sprite "player"` → Game Over
   - **Score hit**: `add_score 10` → Keep playing
   - **Bounce**: `move_player "player" up 20`

```
Example - Collision = Game Over:
┌──────────────────────────────────┐
│ on_collision                     │
│   sprite1: "player"              │
│   sprite2: "obstacle"            │
│   destroy_sprite "player"        │
│   [Display Game Over message]    │
└──────────────────────────────────┘
```

#### Step 5.2: Add Scoring
1. Use `add_score` block in positive collisions
2. Example: Collect bonus items
   ```
   on_collision
     sprite1: "player"
     sprite2: "bonus_star"
     add_score 100
     destroy_sprite "bonus_star"
   ```

---

### Phase 6: Add Game End Conditions

#### Step 6.1: Detect Game Over
Use condition blocks:
```
on_collision (player hit obstacle)
  if health <= 0
    [Stop game]
    [Show "Game Over" message]
```

#### Step 6.2: Detect Win Condition
```
on_timer [1000 ms]
  if score >= 1000
    [Stop game]
    [Show "You Won!" message]
```

---

### Phase 7: Polish & Test

#### Step 7.1: Test Your Game
1. Click **▶️ Play** button in the preview panel
2. Play through your game completely
3. Note any issues:
   - Sprites not appearing?
   - Collisions not working?
   - Game too easy/hard?

#### Step 7.2: Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Sprites not appearing | Check sprite names match (case-sensitive) |
| Collisions not detecting | Make sure both sprites are spawned, check collision block |
| Game too fast | Increase timer intervals or distance values |
| Player invisible | Check X/Y positions are on screen (X: 0-500, Y: 0-600) |

#### Step 7.3: Difficulty Tuning
Adjust these to change difficulty:
- **Obstacle spawn rate**: Decrease timer interval (more frequent)
- **Obstacle speed**: Increase move distance
- **Player speed**: Increase move distance
- **Score threshold**: Make winning score lower (easier) or higher (harder)

---

### Phase 8: Add Polish (Optional)

#### Step 8.1: Add Sound Effects
1. In Asset Manager, click **Upload** → **Sounds**
2. Upload sound files (MP3 or WAV)
3. In code, use `add_sound` blocks when important events happen:
   - Collision sounds
   - Score sounds
   - Game over sounds

#### Step 8.2: Add Visual Feedback
1. **Score Display**: Already visible (built-in)
2. **Particle Effects**: Spawn multiple small sprites on collision
3. **Screen Flash**: Spawn white rectangle briefly when hit

---

### Phase 9: Save & Export

#### Step 9.1: Save to Cloud
1. Click **💾 Save** button
2. Confirm it says "Last saved: now"
3. You can close and reopen later—your game is saved!

#### Step 9.2: Export Code (Optional)
1. Click **📤 Export** button
2. Copy your generated JavaScript code
3. Use in other editors or websites

---

### Phase 10: Publish & Share

#### Step 10.1: Prepare for Publishing
- ✅ Playtest thoroughly
- ✅ Give it a clear, descriptive title
- ✅ Add a brief description

#### Step 10.2: Submit for Publishing
1. Click **🚀 Publish** button
2. Fill in:
   - **Game Title**: Clear name (e.g., "Asteroid Dodger")
   - **Description**: 2-3 sentences about your game
   - **Category**: Choose genre (Action, Puzzle, etc.)
   - **Difficulty**: Easy, Medium, Hard
3. Click **Submit for Review**
4. **Status**: Moderators review within 24-48 hours

#### Step 10.3: After Publishing
✅ Your game appears in global marketplace  
✅ Players can find and play your game  
✅ Earn points on leaderboards  
✅ Get feedback from community  

---

## Best Practices

### ✅ Do This

| Practice | Why | Example |
|----------|-----|---------|
| **Start Simple** | Complexity causes bugs | Start with 1 player + 3 obstacles |
| **Test Frequently** | Catch issues early | Play after every 3-4 block changes |
| **Name Sprites Clearly** | Prevents confusion | "player", "enemy_fast", "bonus_coin" |
| **Use Timers Wisely** | Prevents lag | 50-100ms for updates, 1000ms+ for spawning |
| **Comment Your Logic** | Help future you | "// Spawn obstacle every 2 seconds" |
| **Balance Difficulty** | Keep players engaged | Gradually increase challenge |
| **Use Variables** | Track game state | `health = 3`, `level = 1` |
| **Playtest Multiple Times** | Find hidden bugs | Have friends play your game |

### ❌ Avoid This

| Mistake | Why | Solution |
|---------|-----|----------|
| **Too Many Sprites** | Causes lag/crashes | Keep active sprites under 50 |
| **Infinite Loops** | Freezes game | Always add delays to timers |
| **Forgetting to Destroy** | Memory leaks | Remove off-screen sprites |
| **Poor Feedback** | Confuses players | Always show score, clear win/lose |
| **Unplayable Difficulty** | Players quit | Start easy, ramp up gradually |
| **Unclear Sprite Names** | Broken collisions | Use consistent naming |
| **No Save/Load** | Lose progress | Auto-save is on by default |

### 🎨 Design Tips

**Make Your Game Feel Polished:**

1. **Consistent Colors**: Use 3-5 main colors throughout
2. **Clear Feedback**: Play sounds and animations on events
3. **Progressive Difficulty**: Level 1 is easy, level 5 is hard
4. **Fair Hitboxes**: Don't make collision unfairly punishing
5. **Clear Controls**: Show on-screen instructions
6. **Rewarding Win State**: Celebrate when players succeed

---

## Advanced Features

### 🎲 Multiplayer Gaming

#### What It Is
Play games with friends in real-time on the same server.

#### How to Create Multiplayer
1. Build your game normally
2. Use **Multiplayer Lobby** (🎲 button in header)
3. **Create Room**: Set player limit and game type
4. Share room code with friends
5. Sync actions via network blocks

#### Example: 2-Player Race
- Player 1 controls Left/Right
- Player 2 controls Same keys on different device
- First to reach finish line wins
- Network sync updates positions for both players

### 👥 Social Features

#### Follow Creators
1. Click **👥 Social** button
2. **Discover** tab: Find creators
3. Click **Follow** to stay updated

#### Remix Games
1. Find a game you like in Discover
2. Click **🎨 Remix**
3. Make your own version:
   - Change sprites
   - Adjust difficulty
   - Add new features
4. Save as your own game

### 📊 Creator Dashboard

#### Track Your Success
1. Click **📊 Dashboard** button
2. See metrics:
   - **Total Games**: How many you've published
   - **Total Plays**: How many times played
   - **Followers**: Community size
   - **Revenue**: Earnings (if monetized)
3. **Performance Chart**: Weekly plays trend
4. **Game List**: All your games with stats

#### Use Insights
- Which game is most popular?
- When do people play most?
- What's your biggest audience?
- Adjust future games based on data

### 🏆 Leaderboards

#### What They Are
Global rankings of players by highest score.

#### How to Submit
1. Play a published game
2. Reach a score
3. Game Over screen: Enter your name
4. Click **Submit Score**
5. See your rank on global leaderboard

#### Types of Leaderboards
- **Daily**: Top scores today
- **Weekly**: Top scores this week
- **Monthly**: Top scores this month
- **All-Time**: All-time high scores

#### Compete
- See where you rank globally
- Try to beat other players
- Earn badges/achievements

### ⚙️ Settings & Customization

#### Profile Settings
1. Click **⚙️ Settings** (top-right)
2. **Profile Tab**:
   - Change avatar
   - Edit bio
   - Set role (Player/Developer/Moderator)

#### Editor Preferences
1. **Preferences Tab**:
   - Theme: Dark, Light, Auto
   - Animations: On/Off
   - Snap to Grid: Helpful for alignment
   - Auto-save interval: How often to save

#### Privacy Controls
1. **Privacy Tab**:
   - Profile visibility: Public/Private
   - Show statistics: Yes/No
   - Allow messages: Yes/No
   - Online status: Visible/Hidden

---

## Troubleshooting

### Common Problems & Solutions

#### Issue 1: Game Won't Start
**Symptoms**: Click Play, nothing happens

**Solutions**:
1. Check browser console (F12) for errors
2. Make sure `on_game_start` block exists
3. Verify sprite images uploaded correctly
4. Try refreshing the page (F5)
5. Use different browser (Chrome/Firefox)

#### Issue 2: Sprites Not Appearing
**Symptoms**: Can't see player or obstacles

**Solutions**:
1. Check asset upload—drag image to Asset Manager
2. Verify sprite name in spawn_sprite matches
3. Check X/Y coordinates are on screen:
   - X: 0-500 (left-right)
   - Y: 0-600 (top-bottom)
4. Check sprite size—if 0, it's invisible
5. Make sure sprite upload wasn't blocked by firewall

#### Issue 3: Collisions Not Working
**Symptoms**: Sprites overlap but nothing happens

**Solutions**:
1. Check both sprites exist (use spawn_sprite for both)
2. Verify sprite names in on_collision block match exactly
3. Make sure on_collision block is in workspace
4. Test with larger sprites first (easier to trigger)
5. Check collision logic inside block runs (add debugging)

#### Issue 4: Game Too Slow
**Symptoms**: Stuttering, low FPS (shown in preview)

**Solutions**:
1. Reduce sprite count (destroy old ones faster)
2. Increase timer intervals (fewer updates per second)
3. Simplify sprite graphics (smaller files)
4. Remove unused blocks and assets
5. Close other browser tabs
6. Try different browser

#### Issue 5: Can't Save or Publish
**Symptoms**: Save button doesn't work, or publishing fails

**Solutions**:
1. Check internet connection
2. Login again (session might have expired)
3. Clear browser cache (Ctrl+Shift+Delete)
4. Try incognito/private mode
5. Wait a few minutes and retry
6. Contact support if issue persists

#### Issue 6: Game is Too Easy or Too Hard
**Symptoms**: Winning/losing isn't challenging

**Solutions**:

**Too Easy?**
- Spawn obstacles more frequently
- Increase obstacle speed
- Reduce player speed
- Raise winning score threshold
- Add more obstacles simultaneously

**Too Hard?**
- Spawn obstacles less frequently
- Decrease obstacle speed
- Increase player speed
- Lower winning score threshold
- Add more time before game ends

---

### Debugging Tips

#### Tip 1: Use Console Logging
Enable browser console to see messages:
1. Press **F12** (Developer Tools)
2. Click **Console** tab
3. Look for error messages
4. Messages show which blocks failed

#### Tip 2: Simplify to Find Issues
1. Remove blocks one by one
2. Test after each removal
3. When it works, you found the problem
4. Rebuild from there

#### Tip 3: Test Incrementally
- Add 1-2 blocks
- Play the game
- If it works, add 2 more
- If broken, remove the last 2

#### Tip 4: Check Sprite Names
Names are case-sensitive and must match exactly:
```
✅ Correct:
  spawn_sprite name: "player"
  on_collision sprite1: "player"

❌ Wrong:
  spawn_sprite name: "Player"      (capital P)
  on_collision sprite1: "player"   (won't match)
```

---

## Summary & Next Steps

### What You've Learned

✅ How to use the Blockly editor  
✅ How to upload and manage assets  
✅ How to create player movement  
✅ How to spawn enemies/obstacles  
✅ How to detect collisions  
✅ How to track score and game state  
✅ How to test and publish  
✅ How to use social and multiplayer features  

### Your Learning Path

**Week 1: Master Basics**
- Create 1 simple game (player moves, avoid obstacles)
- Publish and get feedback
- Test on different devices

**Week 2: Add Complexity**
- Add scoring system
- Implement difficulty progression
- Add sound effects

**Week 3: Go Social**
- Try remixing someone else's game
- Follow creators
- Submit to leaderboards

**Week 4: Go Advanced**
- Experiment with multiplayer
- Create complex collision logic
- Analyze dashboard stats

### Your First Game Challenge

**Build "Dodge Master" in 30 minutes:**
1. ⏱️ 5 min: Plan (player moves, obstacles spawn, game over on hit)
2. ⏱️ 10 min: Create player sprite and movement
3. ⏱️ 10 min: Spawn obstacles every 2 seconds
4. ⏱️ 3 min: Add collision detection
5. ⏱️ 2 min: Test and publish

**Next: Improve it!**
- Add scoring
- Increase difficulty over time
- Change sprite graphics
- Submit to leaderboard

### Resources

- **Editor**: https://lupi-fy.com (opens editor)
- **Forum**: Ask questions from community
- **Docs**: In-editor help tooltips on every block
- **AI Assistant**: Click 💬 for instant help
- **Examples**: Remix published games to learn

### Keep Creating! 🚀

Every pro game creator started as a beginner. Your first game won't be perfect—and that's okay! Each game teaches you something new. After 3-5 games, you'll have the skills to create anything.

**The journey of 1,000 games starts with a single block. Go create something amazing!**

---

## Quick-Start Cheat Sheet

Print this page or save it for quick reference while building!

### Essential Block Categories

| Category | Key Blocks | Use For |
|----------|-----------|---------|
| **Events** | on_game_start, on_key_press, on_collision, on_timer | Triggering actions |
| **Actions** | move_player, spawn_sprite, destroy_sprite, add_score | Changing game state |
| **Logic** | if/then, and, or, not | Conditional actions |
| **Math** | +, -, *, /, random(1,10) | Calculations |
| **Variables** | set, change, get | Track data |

### Block Quick Reference

#### Spawn a Sprite
```
spawn_sprite
  name: "player"
  image: [select image]
  at x: 200  y: 400
  size: 50
```

#### Move a Sprite
```
move_player
  sprite: "player"
  direction: left/right/up/down
  distance: 15
```

#### Detect Collision
```
on_collision
  sprite1: "player"
  sprite2: "obstacle"
  [action blocks]
```

#### Add Score
```
add_score 10
```

#### Spawn Every N Seconds
```
on_timer [2000 ms]
  spawn_sprite...
```

### Asset Upload Checklist
- ✅ Image format: PNG with transparent background
- ✅ Image size: 100x100 to 500x500 pixels
- ✅ Sound format: MP3 or WAV
- ✅ File names: Use only letters, numbers, underscores
- ✅ Organization: Upload before using in blocks

### Game Design Checklist
- ✅ Clear goal: Players know how to win
- ✅ Fair controls: Movement feels responsive
- ✅ Progressive difficulty: Starts easy, gets harder
- ✅ Clear feedback: Score, sounds, visuals on events
- ✅ Playable: Takes 1-5 minutes to play
- ✅ Balanced: Not too easy, not too hard

### Before Publishing Checklist
- ✅ Game works from start to end
- ✅ All sprites visible and positioned correctly
- ✅ Collisions detect accurately
- ✅ Score system works
- ✅ Win/lose conditions clear
- ✅ No error messages in console (F12)
- ✅ Tested on multiple devices
- ✅ Descriptive title and description written

### Keyboard Reference

| Key | What It Does |
|-----|--------------|
| **F12** | Open browser console (debugging) |
| **F5** | Refresh page (if game freezes) |
| **Ctrl+S** | Save (manual save) |
| **Arrow Keys** | Player movement (in games) |
| **Space** | Jump/Action (common) |

### Common Variable Names
```
Score: tracks points
Health: player health/lives
Level: difficulty level
Timer: countdown/timer
EnemyCount: number of enemies
PlayerX/PlayerY: position
Speed: movement speed
```

### Tips When Stuck

| Problem | Try This |
|---------|----------|
| Forget syntax | Click **?** on block for help |
| Don't understand block | Ask AI assistant (💬) |
| Game crashes | Simplify—remove last 2 blocks |
| Can't fix bug | Save, refresh, reopen project |
| Lost your work | Check autosave (usually on) |

### Recommended First Games (Easy → Hard)

1. **Dodge Master** (30 min)
   - Player moves left/right
   - Obstacles fall down
   - Avoid = score, hit = game over

2. **Color Match** (1 hour)
   - Click matching colors
   - Timer counts down
   - Score increases

3. **Platformer Basics** (2 hours)
   - Player jumps over platforms
   - Reach the goal
   - Collect coins for points

4. **Space Shooter** (3 hours)
   - Player shoots projectiles
   - Enemies spawn and attack
   - Survive longest or reach score

5. **Multiplayer Race** (4+ hours)
   - Two players compete
   - First to finish wins
   - Network sync positions

---

## Final Notes

**Remember:**
- Every block has documentation—hover for help
- Your first game won't be perfect—that's expected
- The best way to learn is by building
- Test constantly and get feedback
- Ask the AI assistant for help anytime
- Join the community and remix others' games

**You have everything you need to create amazing 2D games. Let's go make something great!** 🎮✨

---

### Quick Links

- 📧 **Email Support**: support@lupi-fy.com
- 💬 **Community Forum**: https://lupi-fy.com/forum
- 🤖 **AI Helper**: Click the chat icon in the editor
- 📚 **Block Documentation**: Hover on blocks or click **?**
- 🎮 **Example Games**: Browse and remix games to learn

---

**Last Updated**: December 2025  
**Version**: 1.0 Complete Guide  
**Status**: Ready for All Users ✅
