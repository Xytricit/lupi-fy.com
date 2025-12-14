# Games URLs (games/urls.py)

## File Overview
**Path:** `games/urls.py`  
**Lines:** 68  
**Purpose:** Game editor, multiplayer gaming, and game creator tools

---

## Core URL Patterns

### Game Editor Routes

#### 1. Recently Played API
```python
path('api/recently-played/', views.recently_played_api, name='recently_played_api')
```
**Name:** `recently_played_api`  
**Method:** GET  
**Purpose:** Get user's recently played games  
**View:** `recently_played_api`  
**Response:** JSON list of games

#### 2. Game Editor
```python
path('editor/', views.editor_view, name='editor')
```
**Name:** `editor`  
**Purpose:** Main game editor/creator interface  
**View:** `editor_view`  
**Usage:** Where creators build and design games

#### 3. Editor Debug Mode
```python
path('editor-debug/', views.editor_debug_view, name='editor_debug')
```
**Name:** `editor_debug`  
**Purpose:** Debug version of editor with dev tools  
**View:** `editor_debug_view`  
**Usage:** Development/testing only

#### 4. Editor Enhanced
```python
path('editor-enhanced/', views.editor_view, {'version': 'enhanced'}, name='editor_enhanced')
```
**Name:** `editor_enhanced`  
**Purpose:** Enhanced editor version with additional features  
**View:** `editor_view` with `version='enhanced'` parameter  
**Usage:** Advanced creator features

#### 5. Editor Guest/Public
```python
path('editor-guest/', views.editor_public_view, name='editor_guest')
```
**Name:** `editor_guest`  
**Purpose:** Public game editor (for non-logged-in users or remixes)  
**View:** `editor_public_view`  
**Usage:** Play and remix published games

---

### Dashboard Routes

#### 6. Editor Dashboard
```python
path('dashboard/', views.editor_dashboard_view, name='dashboard')
```
**Name:** `dashboard`  
**Purpose:** Lists user's games, drafts, analytics  
**View:** `editor_dashboard_view`  
**Note:** Different from accounts `dashboard` (which is user dashboard)

#### 7. Games Dashboard Home
```python
path('dashboard/home/', views.dashboard_home_view, name='games_dashboard_home')
```
**Name:** `games_dashboard_home`  
**Purpose:** Games section home/overview  
**View:** `dashboard_home_view`  
**CRITICAL:** Renamed from `dashboard_home` to avoid URL collision with accounts app

---

### Multiplayer & Tutorial

#### 8. Multiplayer
```python
path('multiplayer/', views.multiplayer_view, name='multiplayer')
```
**Name:** `multiplayer`  
**Purpose:** Multiplayer game lobby/session view  
**View:** `multiplayer_view`

#### 9. Tutorial
```python
path('tutorial/', views.tutorial_view, name='tutorial')
```
**Name:** `tutorial`  
**Purpose:** Game creation tutorial  
**View:** `tutorial_view`

#### 10. Moderation
```python
path('moderation/', views.moderation_view, name='moderation')
```
**Name:** `moderation`  
**Purpose:** Game moderation queue for admins  
**View:** `moderation_view`

---

### Game Management APIs

#### 11. Save Game API
```python
path('api/save/', views.save_game_api, name='save_game')
```
**Name:** `save_game`  
**Method:** POST  
**Purpose:** Save game draft/progress  
**View:** `save_game_api`

#### 12. Publish Game API
```python
path('api/publish/', views.publish_game_api, name='publish_game')
```
**Name:** `publish_game`  
**Method:** POST  
**Purpose:** Publish game to platform  
**View:** `publish_game_api`

#### 13. Approve Game API
```python
path('api/approve/', views.approve_game_api, name='approve_game')
```
**Name:** `approve_game`  
**Method:** POST  
**Purpose:** Admin approval of game (moderation)  
**View:** `approve_game_api`

#### 14. Reject Game API
```python
path('api/reject/', views.reject_game_api, name='reject_game')
```
**Name:** `reject_game`  
**Method:** POST  
**Purpose:** Reject game submission  
**View:** `reject_game_api`

#### 15. Games List API
```python
path('api/games-list/', views.games_list_api, name='games_list')
```
**Name:** `games_list`  
**Method:** GET  
**Purpose:** Get list of all games (with filters)  
**View:** `games_list_api`  
**Query Params:** category, sort, page, search

---

### Asset Management APIs

#### 16. Upload Asset API
```python
path('api/upload-asset/', views.upload_asset_api, name='upload_asset')
```
**Name:** `upload_asset`  
**Method:** POST  
**Purpose:** Upload image/sprite/sound asset  
**View:** `upload_asset_api`  
**Content:** Multipart form data with file

#### 17. List Assets API
```python
path('api/list-assets/', views.list_assets_api, name='list_assets')
```
**Name:** `list_assets`  
**Method:** GET  
**Purpose:** List creator's uploaded assets  
**View:** `list_assets_api`  
**Response:** JSON list with URLs

---

### Score & Leaderboard APIs

#### 18. Submit Score API
```python
path('api/submit-score/', views.submit_score_api, name='submit_score')
```
**Name:** `submit_score`  
**Method:** POST  
**Purpose:** Submit game score/results  
**View:** `submit_score_api`  
**Data:** score, time_played, game_id

#### 19. Leaderboard API
```python
path('api/leaderboard/', views.leaderboard_api, name='leaderboard')
```
**Name:** `leaderboard`  
**Method:** GET  
**Purpose:** Get game leaderboard  
**View:** `leaderboard_api`  
**Query Params:** game_id, limit

---

### User Achievement & Analytics APIs

#### 20. User Achievements API
```python
path('api/achievements/', views.user_achievements_api, name='user_achievements')
```
**Name:** `user_achievements`  
**Method:** GET  
**Purpose:** Get user's earned achievements/badges  
**View:** `user_achievements_api`

#### 21. Analyze Logic API
```python
path('api/analyze-logic/', views.analyze_logic_api, name='analyze_logic')
```
**Name:** `analyze_logic`  
**Method:** POST  
**Purpose:** AI analysis of game logic/code  
**View:** `analyze_logic_api`  
**Data:** game_code, logic_blocks

#### 22. Creator Revenue API
```python
path('api/creator-revenue/', views.creator_revenue_api, name='creator_revenue')
```
**Name:** `creator_revenue`  
**Method:** GET  
**Purpose:** Creator earnings/monetization stats  
**View:** `creator_revenue_api`

---

## Advanced Features (views_advanced)

### Multiplayer Sessions

#### 23. Create Multiplayer Session
```python
path('api/multiplayer/create-session/', views_advanced.create_multiplayer_session, name='create_session')
```
**Name:** `create_session`  
**Method:** POST  
**Purpose:** Start new multiplayer game session  
**View:** `create_multiplayer_session`  
**Data:** game_id, max_players, settings

#### 24. Join Multiplayer Session
```python
path('api/multiplayer/join-session/', views_advanced.join_multiplayer_session, name='join_session')
```
**Name:** `join_session`  
**Method:** POST  
**Purpose:** Join existing multiplayer session  
**View:** `join_multiplayer_session`  
**Data:** session_id, player_name

#### 25. List Active Sessions
```python
path('api/multiplayer/active-sessions/', views_advanced.list_active_sessions, name='active_sessions')
```
**Name:** `active_sessions`  
**Method:** GET  
**Purpose:** Get available multiplayer sessions  
**View:** `list_active_sessions`  
**Response:** JSON list of active games

---

### AI Assistant Features

#### 26. AI Suggest Improvements
```python
path('api/ai/suggest-improvements/', views_advanced.ai_suggest_improvements, name='ai_suggestions')
```
**Name:** `ai_suggestions`  
**Method:** POST  
**Purpose:** Get AI suggestions for game improvement  
**View:** `ai_suggest_improvements`

#### 27. AI Generate Starter Code
```python
path('api/ai/generate-starter/', views_advanced.ai_generate_starter_code, name='ai_starter')
```
**Name:** `ai_starter`  
**Method:** POST  
**Purpose:** Generate starter game code  
**View:** `ai_generate_starter_code`

---

### Moderation Features

#### 28. Report Game
```python
path('api/moderation/report-game/', views_advanced.report_game, name='report_game')
```
**Name:** `report_game`  
**Method:** POST  
**Purpose:** Report inappropriate game  
**View:** `report_game`  
**Data:** game_id, reason

#### 29. Moderation Queue
```python
path('api/moderation/queue/', views_advanced.get_moderation_queue, name='mod_queue')
```
**Name:** `mod_queue`  
**Method:** GET  
**Purpose:** Get games pending moderation  
**View:** `get_moderation_queue`  
**Admin Only:** Yes

#### 30. Add Game Tag
```python
path('api/moderation/add-tag/', views_advanced.add_game_tag, name='add_tag')
```
**Name:** `add_tag`  
**Method:** POST  
**Purpose:** Add category/tag to game  
**View:** `add_game_tag`

---

### Creator Analytics

#### 31. Creator Game Stats
```python
path('api/creator/game-stats/', views_advanced.creator_game_stats, name='game_stats')
```
**Name:** `game_stats`  
**Method:** GET  
**Purpose:** Get analytics for creator's games  
**View:** `creator_game_stats`

#### 32. Creator Dashboard Data
```python
path('api/creator/dashboard/', views_advanced.creator_dashboard_data, name='dashboard')
```
**Name:** `dashboard`  
**Method:** GET  
**Purpose:** Creator dashboard analytics  
**View:** `creator_dashboard_data`  
**Note:** URL name collision (see note below)

---

### User Game Management

#### 33. User Games API
```python
path('api/user/games/', views_advanced.user_games_api, name='user_games_api')
```
**Name:** `user_games_api`  
**Method:** GET  
**Purpose:** Get user's created games  
**View:** `user_games_api`

#### 34. Create Game API
```python
path('api/create/', views_advanced.create_game_api, name='create_game')
```
**Name:** `create_game`  
**Method:** POST  
**Purpose:** Create new game  
**View:** `create_game_api`

#### 35. Delete Game API
```python
path('api/delete/', views_advanced.delete_game_api, name='delete_game')
```
**Name:** `delete_game`  
**Method:** POST  
**Purpose:** Delete game  
**View:** `delete_game_api`

#### 36. Share Game API
```python
path('api/share/', views_advanced.share_game_api, name='share_game')
```
**Name:** `share_game`  
**Method:** POST  
**Purpose:** Share game link  
**View:** `share_game_api`

---

### Notification Management

#### 37. Get Notifications
```python
path('api/notifications/', views_advanced.get_notifications, name='get_notifications')
```
**Name:** `get_notifications`  
**Method:** GET  
**Purpose:** Get game-related notifications  
**View:** `get_notifications`

#### 38. Mark Notification Read
```python
path('api/notifications/mark-read/', views_advanced.mark_notification_read, name='mark_read')
```
**Name:** `mark_read`  
**Method:** POST  
**Purpose:** Mark notification as read  
**View:** `mark_notification_read`

---

### User Profile & Social

#### 39. Get User Profile
```python
path('api/user/<str:username>/', views_advanced.get_user_profile, name='user_profile')
```
**Name:** `user_profile`  
**URL Parameter:** `username` (str)  
**Method:** GET  
**Purpose:** Get user profile data  
**View:** `get_user_profile`

#### 40. Follow User
```python
path('api/user/follow/', views_advanced.follow_user, name='follow_user')
```
**Name:** `follow_user`  
**Method:** POST  
**Purpose:** Follow/unfollow creator  
**View:** `follow_user`

#### 41. Update User Profile
```python
path('api/user/profile-update/', views_advanced.update_user_profile, name='profile_update')
```
**Name:** `profile_update`  
**Method:** POST  
**Purpose:** Update user profile  
**View:** `update_user_profile`

---

### Game Remixing

#### 42. Remix Game
```python
path('api/remix/', views_advanced.remix_game, name='remix_game')
```
**Name:** `remix_game`  
**Method:** POST  
**Purpose:** Create remix of existing game  
**View:** `remix_game`  
**Data:** game_id, new_name

---

## URL Name Reference Table

| URL Name | Pattern | View | Parameters | Method |
|----------|---------|------|------------|--------|
| `recently_played_api` | `/games/api/recently-played/` | `recently_played_api` | - | GET |
| `editor` | `/games/editor/` | `editor_view` | - | GET |
| `editor_debug` | `/games/editor-debug/` | `editor_debug_view` | - | GET |
| `editor_enhanced` | `/games/editor-enhanced/` | `editor_view` | version=enhanced | GET |
| `editor_guest` | `/games/editor-guest/` | `editor_public_view` | - | GET |
| `dashboard` | `/games/dashboard/` | `editor_dashboard_view` | - | GET |
| `games_dashboard_home` | `/games/dashboard/home/` | `dashboard_home_view` | - | GET |
| `multiplayer` | `/games/multiplayer/` | `multiplayer_view` | - | GET |
| `tutorial` | `/games/tutorial/` | `tutorial_view` | - | GET |
| `moderation` | `/games/moderation/` | `moderation_view` | - | GET |
| `save_game` | `/games/api/save/` | `save_game_api` | - | POST |
| `publish_game` | `/games/api/publish/` | `publish_game_api` | - | POST |
| `approve_game` | `/games/api/approve/` | `approve_game_api` | - | POST |
| `reject_game` | `/games/api/reject/` | `reject_game_api` | - | POST |
| `games_list` | `/games/api/games-list/` | `games_list_api` | - | GET |
| `upload_asset` | `/games/api/upload-asset/` | `upload_asset_api` | - | POST |
| `list_assets` | `/games/api/list-assets/` | `list_assets_api` | - | GET |
| `submit_score` | `/games/api/submit-score/` | `submit_score_api` | - | POST |
| `leaderboard` | `/games/api/leaderboard/` | `leaderboard_api` | - | GET |
| `user_achievements` | `/games/api/achievements/` | `user_achievements_api` | - | GET |
| `analyze_logic` | `/games/api/analyze-logic/` | `analyze_logic_api` | - | POST |
| `creator_revenue` | `/games/api/creator-revenue/` | `creator_revenue_api` | - | GET |
| `create_session` | `/games/api/multiplayer/create-session/` | `create_multiplayer_session` | - | POST |
| `join_session` | `/games/api/multiplayer/join-session/` | `join_multiplayer_session` | - | POST |
| `active_sessions` | `/games/api/multiplayer/active-sessions/` | `list_active_sessions` | - | GET |
| `ai_suggestions` | `/games/api/ai/suggest-improvements/` | `ai_suggest_improvements` | - | POST |
| `ai_starter` | `/games/api/ai/generate-starter/` | `ai_generate_starter_code` | - | POST |
| `report_game` | `/games/api/moderation/report-game/` | `report_game` | - | POST |
| `mod_queue` | `/games/api/moderation/queue/` | `get_moderation_queue` | - | GET |
| `add_tag` | `/games/api/moderation/add-tag/` | `add_game_tag` | - | POST |
| `game_stats` | `/games/api/creator/game-stats/` | `creator_game_stats` | - | GET |
| `dashboard` | `/games/api/creator/dashboard/` | `creator_dashboard_data` | - | GET |
| `user_games_api` | `/games/api/user/games/` | `user_games_api` | - | GET |
| `create_game` | `/games/api/create/` | `create_game_api` | - | POST |
| `delete_game` | `/games/api/delete/` | `delete_game_api` | - | POST |
| `share_game` | `/games/api/share/` | `share_game_api` | - | POST |
| `get_notifications` | `/games/api/notifications/` | `get_notifications` | - | GET |
| `mark_read` | `/games/api/notifications/mark-read/` | `mark_notification_read` | - | POST |
| `user_profile` | `/games/api/user/<username>/` | `get_user_profile` | username | GET |
| `follow_user` | `/games/api/user/follow/` | `follow_user` | - | POST |
| `profile_update` | `/games/api/user/profile-update/` | `update_user_profile` | - | POST |
| `remix_game` | `/games/api/remix/` | `remix_game` | - | POST |

---

## Critical Notes

### URL Name Collision Fixed ⚠️
**Problem:** Both `core` app and `games` app had identical URL name `dashboard_home`

**Solution Applied:**
- **BEFORE:** `games` URL: `path('dashboard/home/', views.dashboard_home_view, name='dashboard_home')`
- **AFTER:** `games` URL: `path('dashboard/home/', views.dashboard_home_view, name='games_dashboard_home')`

**Why:** Django's URL resolver uses the last-registered app when duplicate names exist. The `games` version was overriding the core dashboard. Fixed by making games URL unique.

---

## URL Patterns Organization

### Editor Routes (5 patterns)
Game creation and editing interfaces

### Dashboard Routes (2 patterns)
Game creator dashboards and overviews

### Core Game Features (15 patterns)
Save, publish, scores, analytics, assets

### Advanced Features (27 patterns)
Multiplayer, AI, moderation, social, remixing

### Total: 42 URL patterns

---

## Authentication & Permissions

All game URLs require user authentication except:
- `editor_guest` - Public game playing
- Some read-only API endpoints may be public

Admin/Creator-only endpoints:
- `moderation` - Admin moderation panel
- `approve_game`, `reject_game` - Admin actions
- `mod_queue` - Admin queue

---

## API Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### List Response
```json
{
  "results": [ ... ],
  "count": 10,
  "next": "/games/api/games-list/?page=2",
  "previous": null
}
```

---

## Template Usage Examples

```html
<!-- Link to game editor -->
<a href="{% url 'editor' %}">Create Game</a>

<!-- Link to games dashboard home -->
<a href="{% url 'games_dashboard_home' %}">My Games</a>

<!-- Multiplayer session -->
<a href="{% url 'multiplayer' %}">Play Multiplayer</a>

<!-- Create new game -->
<form action="{% url 'create_game' %}" method="POST">
  {% csrf_token %}
  <!-- form fields -->
</form>

<!-- User game profile -->
<a href="{% url 'user_profile' username=creator.username %}">
  View {{ creator.username }}'s Games
</a>
```
