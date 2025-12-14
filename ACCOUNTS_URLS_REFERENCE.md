# Accounts URLs (accounts/urls.py)

## File Overview
**Path:** `accounts/urls.py`  
**Lines:** 111  
**Purpose:** User authentication, profile, subscription, chat, notifications, and appearance settings

---

## URL Patterns

### Authentication Routes

#### 1. Google OAuth Login
```python
path("login/", views.google_login_view, name="login")
```
**Name:** `login`  
**Purpose:** Google OAuth login page (replaces old register/login)  
**View:** `google_login_view`

#### 2. Local Login Fallback
```python
path("login/local/", views.login_view, name="local_login")
```
**Name:** `local_login`  
**Purpose:** Traditional local login when OAuth unavailable  
**View:** `login_view`

#### 3. Registration
```python
path("register/", views.register_view, name="register")
```
**Name:** `register`  
**Purpose:** Handles both Google OAuth and local signup  
**View:** `register_view`

#### 4. Logout
```python
path("logout/", views.logout_view, name="logout")
```
**Name:** `logout`  
**Purpose:** User logout  
**View:** `logout_view`

---

### User Dashboard & Profile Routes

#### 5. Dashboard
```python
path("dashboard/", views.dashboard_view, name="dashboard")
```
**Name:** `dashboard`  
**Purpose:** User dashboard/home (not the games creator dashboard)  
**View:** `dashboard_view`

#### 6. Profile Page
```python
path("profile/", views.profile_view, name="profile")
```
**Name:** `profile`  
**Purpose:** User's own profile editing  
**View:** `profile_view`

#### 7. Subscriptions
```python
path("subscriptions/", views.subscriptions_view, name="subscriptions")
```
**Name:** `subscriptions`  
**Purpose:** View/manage subscriptions to creators and communities  
**View:** `subscriptions_view`

#### 8. Account Dashboard
```python
path("account/", views.account_dashboard_view, name="account_dashboard")
```
**Name:** `account_dashboard`  
**Purpose:** Account settings and preferences  
**View:** `account_dashboard_view`

---

### Subscription Management

#### 9. Toggle Community Subscription
```python
path(
    "toggle-subscription/<int:community_id>/",
    views.toggle_subscription,
    name="toggle_subscription",
)
```
**Name:** `toggle_subscription`  
**URL Parameter:** `community_id` (int)  
**Purpose:** Subscribe/unsubscribe from community  
**View:** `toggle_subscription`

#### 10. Toggle Author Subscription
```python
path(
    "toggle-subscription/author/<int:author_id>/",
    views.toggle_subscription,
    name="toggle_subscription_author",
)
```
**Name:** `toggle_subscription_author`  
**URL Parameter:** `author_id` (int)  
**Purpose:** Subscribe/unsubscribe from content creator  
**View:** `toggle_subscription`

---

### User Profile Views

#### 11. User Profile Popup/Card
```python
path(
    "user/<int:user_id>/profile/", 
    views.user_profile_view, 
    name="user_profile_view"
)
```
**Name:** `user_profile_view`  
**URL Parameter:** `user_id` (int)  
**Purpose:** Hover card/modal with user info  
**View:** `user_profile_view`  
**Usage:** Displayed when hovering over author name

#### 12. Public Profile Page
```python
path(
    "user/<int:user_id>/public-profile/",
    views.public_profile_view,
    name="public_profile_view",
)
```
**Name:** `public_profile_view`  
**URL Parameter:** `user_id` (int)  
**Purpose:** Full public profile page  
**View:** `public_profile_view`  
**Usage:** Click profile name to view full page

---

### Chat Routes

#### 13. Chat Page (All Conversations)
```python
path("chat/", views.chat_page_view, name="chat_page")
```
**Name:** `chat_page`  
**Purpose:** Main chat/messaging page  
**View:** `chat_page_view`

#### 14. Chat with Specific User
```python
path("chat/<int:user_id>/", views.chat_page_view, name="chat_with_user")
```
**Name:** `chat_with_user`  
**URL Parameter:** `user_id` (int)  
**Purpose:** Open chat with specific user  
**View:** `chat_page_view`  
**Usage:** `{% url 'chat_with_user' user_id=123 %}`

#### 15. Send Message API
```python
path("api/send-message/", views.send_message_view, name="send_message")
```
**Name:** `send_message`  
**Method:** POST  
**Purpose:** Submit new chat message  
**View:** `send_message_view`

#### 16. Get Messages API
```python
path("api/get-messages/", views.get_messages_view, name="get_messages")
```
**Name:** `get_messages`  
**Method:** GET  
**Purpose:** Load message history  
**View:** `get_messages_view`

#### 17. Get Conversations API
```python
path(
    "api/get-conversations/", 
    views.get_conversations_view, 
    name="get_conversations"
)
```
**Name:** `get_conversations`  
**Method:** GET  
**Purpose:** Load list of open conversations  
**View:** `get_conversations_view`

#### 18. Block User API
```python
path("api/block-user/", views.block_user_api, name="block_user_api")
```
**Name:** `block_user_api`  
**Method:** POST  
**Purpose:** Block user from messaging  
**View:** `block_user_api`

---

### Notification Routes

#### 19. Notifications Page
```python
path("notifications/", views.notifications_page_view, name="notifications_page")
```
**Name:** `notifications_page`  
**Purpose:** Full notifications page  
**View:** `notifications_page_view`

#### 20. Get Notifications API
```python
path(
    "api/notifications/", 
    views.get_notifications_api, 
    name="get_notifications_api"
)
```
**Name:** `get_notifications_api`  
**Method:** GET  
**Purpose:** Load recent notifications  
**View:** `get_notifications_api`  
**Used by:** `/notifications/api/recent/` endpoint called in dashboard.js

#### 21. Mark Notification Read
```python
path(
    "api/notifications/<int:notif_id>/mark-read/",
    views.mark_notification_read_api,
    name="mark_notification_read",
)
```
**Name:** `mark_notification_read`  
**URL Parameter:** `notif_id` (int)  
**Purpose:** Mark single notification as read  
**View:** `mark_notification_read_api`

---

### Game Lobby Routes

#### 22. Game Lobby
```python
path("game/lobby/", views.game_lobby_view, name="game_lobby")
```
**Name:** `game_lobby`  
**Purpose:** Multiplayer game lobby/chat  
**View:** `game_lobby_view`

#### 23. Game Lobby Post Message
```python
path(
    "api/game/post-message/",
    views.game_lobby_post_message_view,
    name="game_post_message",
)
```
**Name:** `game_post_message`  
**Method:** POST  
**Purpose:** Send message in game lobby  
**View:** `game_lobby_post_message_view`

---

### Games Hub Routes

#### 24. Games Hub
```python
path("games/", views.games_hub_view, name="games_hub")
```
**Name:** `games_hub`  
**Purpose:** Browse all games  
**View:** `games_hub_view`  
**Note:** This is in accounts app, different from games app endpoints

---

### Letter Set Game Routes

#### 25. Letter Set Game
```python
path("games/letter-set/", views.letter_set_game_view, name="letter_set_game")
```
**Name:** `letter_set_game`  
**Purpose:** Play letter set word game  
**View:** `letter_set_game_view`

#### 26. Submit Word
```python
path(
    "api/game/letter-set/submit-word/",
    views.letter_set_submit_word_view,
    name="letter_set_submit_word",
)
```
**Name:** `letter_set_submit_word`  
**Method:** POST  
**Purpose:** Submit word in letter set game  
**View:** `letter_set_submit_word_view`

#### 27. Letter Set Chat
```python
path(
    "api/game/letter-set/chat/", 
    views.letter_set_chat_view, 
    name="letter_set_chat"
)
```
**Name:** `letter_set_chat`  
**Purpose:** Game chat/multiplayer messaging  
**View:** `letter_set_chat_view`

#### 28. Letter Set Start
```python
path(
    "api/game/letter-set/start/",
    views.letter_set_start_view,
    name="letter_set_start",
)
```
**Name:** `letter_set_start`  
**Purpose:** Start new letter set game session  
**View:** `letter_set_start_view`

---

### Game Challenge Routes

#### 29. Game Challenge Start
```python
path(
    "api/game/challenge/start/",
    views.game_lobby_challenge_start_view,
    name="game_challenge_start",
)
```
**Name:** `game_challenge_start`  
**Purpose:** Start 12-word challenge from lobby  
**View:** `game_lobby_challenge_start_view`

#### 30. Game Challenge Save
```python
path(
    "api/game/challenge/save/",
    views.game_lobby_challenge_save_view,
    name="game_challenge_save",
)
```
**Name:** `game_challenge_save`  
**Purpose:** Save challenge progress/score  
**View:** `game_lobby_challenge_save_view`

---

### Creator Routes

#### 31. Creator Dashboard
```python
path("creators/", views.creator_dashboard_view, name="creator_dashboard")
```
**Name:** `creator_dashboard`  
**Purpose:** Creator analytics and earnings  
**View:** `creator_dashboard_view`

#### 32. Post Analytics API
```python
path(
    "api/post-analytics/<int:post_id>/",
    views.post_analytics_api,
    name="post_analytics_api",
)
```
**Name:** `post_analytics_api`  
**URL Parameter:** `post_id` (int)  
**Purpose:** Get analytics for specific post  
**View:** `post_analytics_api`

#### 33. Creator Chat API
```python
path("api/creator-chat/", views.creator_chat_api, name="creator_chat_api")
```
**Name:** `creator_chat_api`  
**Purpose:** Chat with fans/community  
**View:** `creator_chat_api`

---

### Settings & Appearance

#### 34. Appearance Settings
```python
path("appearance/", views.appearance_view, name="appearance")
```
**Name:** `appearance`  
**Purpose:** User appearance/theme settings  
**View:** `appearance_view`  
**Method:** GET (load form) / POST (save preferences)  
**Used by:** Theme switching in dashboard.js

---

## Static Files Configuration

```python
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
Serves media files (avatars, images) under `/media/` URL

---

## URL Name Reference Table

| URL Name | Pattern | View | Parameters |
|----------|---------|------|------------|
| `login` | `/accounts/login/` | `google_login_view` | - |
| `local_login` | `/accounts/login/local/` | `login_view` | - |
| `register` | `/accounts/register/` | `register_view` | - |
| `logout` | `/accounts/logout/` | `logout_view` | - |
| `dashboard` | `/accounts/dashboard/` | `dashboard_view` | - |
| `profile` | `/accounts/profile/` | `profile_view` | - |
| `subscriptions` | `/accounts/subscriptions/` | `subscriptions_view` | - |
| `account_dashboard` | `/accounts/account/` | `account_dashboard_view` | - |
| `toggle_subscription` | `/accounts/toggle-subscription/<id>/` | `toggle_subscription` | `community_id` |
| `toggle_subscription_author` | `/accounts/toggle-subscription/author/<id>/` | `toggle_subscription` | `author_id` |
| `user_profile_view` | `/accounts/user/<id>/profile/` | `user_profile_view` | `user_id` |
| `public_profile_view` | `/accounts/user/<id>/public-profile/` | `public_profile_view` | `user_id` |
| `chat_page` | `/accounts/chat/` | `chat_page_view` | - |
| `chat_with_user` | `/accounts/chat/<id>/` | `chat_page_view` | `user_id` |
| `send_message` | `/accounts/api/send-message/` | `send_message_view` | - |
| `get_messages` | `/accounts/api/get-messages/` | `get_messages_view` | - |
| `get_conversations` | `/accounts/api/get-conversations/` | `get_conversations_view` | - |
| `block_user_api` | `/accounts/api/block-user/` | `block_user_api` | - |
| `notifications_page` | `/accounts/notifications/` | `notifications_page_view` | - |
| `get_notifications_api` | `/accounts/api/notifications/` | `get_notifications_api` | - |
| `mark_notification_read` | `/accounts/api/notifications/<id>/mark-read/` | `mark_notification_read_api` | `notif_id` |
| `game_lobby` | `/accounts/game/lobby/` | `game_lobby_view` | - |
| `game_post_message` | `/accounts/api/game/post-message/` | `game_lobby_post_message_view` | - |
| `games_hub` | `/accounts/games/` | `games_hub_view` | - |
| `letter_set_game` | `/accounts/games/letter-set/` | `letter_set_game_view` | - |
| `letter_set_submit_word` | `/accounts/api/game/letter-set/submit-word/` | `letter_set_submit_word_view` | - |
| `letter_set_chat` | `/accounts/api/game/letter-set/chat/` | `letter_set_chat_view` | - |
| `letter_set_start` | `/accounts/api/game/letter-set/start/` | `letter_set_start_view` | - |
| `game_challenge_start` | `/accounts/api/game/challenge/start/` | `game_lobby_challenge_start_view` | - |
| `game_challenge_save` | `/accounts/api/game/challenge/save/` | `game_lobby_challenge_save_view` | - |
| `creator_dashboard` | `/accounts/creators/` | `creator_dashboard_view` | - |
| `post_analytics_api` | `/accounts/api/post-analytics/<id>/` | `post_analytics_api` | `post_id` |
| `creator_chat_api` | `/accounts/api/creator-chat/` | `creator_chat_api` | - |
| `appearance` | `/accounts/appearance/` | `appearance_view` | - |

---

## Important Notes

1. **NOT DUPLICATED:** The `accounts` app has NO duplicate URL names with other apps
2. **login vs local_login:** `login` is OAuth, `local_login` is fallback
3. **dashboard:** This is the main user dashboard, different from `games_dashboard_home`
4. **User ID Parameters:** Always use `user_id` in URL names
5. **Post Analytics:** Used to track engagement metrics
6. **Static Files:** Media serving configured at end of file
7. **All Patterns:** Begin with `/accounts/` base path

---

## URL Tags in Templates

Examples of how to use these URL names in Django templates:

```html
<!-- Authentication -->
<a href="{% url 'login' %}">Sign In</a>
<a href="{% url 'register' %}">Sign Up</a>

<!-- User Profile -->
<a href="{% url 'public_profile_view' user_id=user.id %}">View Profile</a>

<!-- Chat -->
<a href="{% url 'chat_with_user' user_id=author_id %}">Message</a>

<!-- Subscriptions -->
<form method="post">
  {% csrf_token %}
  <button formaction="{% url 'toggle_subscription' community_id=community.id %}">
    Subscribe
  </button>
</form>

<!-- Creator -->
<a href="{% url 'creator_dashboard' %}">Creator Hub</a>

<!-- Settings -->
<a href="{% url 'appearance' %}">Appearance</a>
```

---

## API Endpoint Structure

Many accounts URLs provide JSON APIs for AJAX requests:
- POST endpoints for actions (send message, toggle subscription)
- GET endpoints for data fetching (get notifications, get conversations)
- All include CSRF token validation
- Return JSON responses for frontend handling
