# 🎮 LUPI-FY COMPLETE APP REPORT
**Comprehensive Documentation for AI-Assisted Development**

**Generated:** December 13, 2025  
**Framework:** Django 4.2.27 + Channels 4.1.0  
**Database:** SQLite/PostgreSQL  
**Frontend:** HTML5, Vanilla JS, Tailwind CSS, Blockly, Phaser 3.60  

---

## TABLE OF CONTENTS
1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Complete File Structure](#complete-file-structure)
4. [Django Apps & Models](#django-apps--models)
5. [HTML Templates (Complete List)](#html-templates-complete-list)
6. [URL Routing](#url-routing)
7. [Static Assets](#static-assets)
8. [Database Schema](#database-schema)
9. [API Endpoints](#api-endpoints)
10. [Key Features](#key-features)
11. [Developer Guide for AI](#developer-guide-for-ai)

---

## PROJECT OVERVIEW

### What is Lupi-fy?
**Lupi-fy** is a comprehensive web platform that enables users to:
- 🎮 Create 2D games visually using Blockly (drag-and-drop blocks)
- 📊 Manage game assets (sprites, sounds, backgrounds)
- 🏆 Submit and track game scores on leaderboards
- 👥 Build communities and follow creators
- 📝 Create and share blog posts
- 💬 Use AI-powered chatbot assistance
- 🎯 Monetize games and track creator analytics

### Core User Personas
1. **Game Creators**: Design games with no coding experience
2. **Players**: Discover, play, and compete on leaderboards
3. **Community Managers**: Create and manage communities
4. **Content Creators**: Write blog posts and articles
5. **Moderators**: Review and approve game content
6. **Administrators**: Manage platform operations

### Key Statistics
- **6 Django Apps**: accounts, blog, communities, core, games, recommend, chatbot
- **46+ HTML Templates**: Across multiple modules
- **4 JavaScript Bundles**: Game engine, websocket, dashboard, chatbot
- **Multiple CSS Files**: Component, dashboard, inline styles
- **3 Major Features**: Games, Communities, Blog

---

## ARCHITECTURE & TECHNOLOGY STACK

### Frontend Architecture
```
HTML5 Templates (Django)
    ↓
Vanilla JavaScript + Libraries
    ├── Blockly 11.3.0 (Block-based coding)
    ├── Phaser 3.60.0 (2D Game Engine)
    ├── Chart.js (Analytics dashboards)
    └── Tailwind CSS (Styling)
    ↓
WebSocket (Channels 4.1.0) & Fetch API
    ↓
Backend APIs
```

### Backend Architecture
```
Django 4.2.27 (ASGI + WSGI)
    ├── Django REST Framework (for APIs)
    ├── Django Channels (WebSockets)
    ├── Django-allauth (OAuth/Authentication)
    └── WhiteNoise (Static file serving)
    ↓
SQLite/PostgreSQL Database
```

### Deployment
- **Hosting**: Render.com (render.yaml config)
- **Server**: Gunicorn + Daphne
- **Static Files**: WhiteNoise middleware

### Dependencies (requirements.txt)
```
Django==4.2.27
Channels==4.1.0
Gunicorn==23.0.0
BeautifulSoup4==4.12.2
WebSockets==11.0.3
asgiref==3.11.0
whitenoise==6.11.0
```

---

## COMPLETE FILE STRUCTURE

### Root Level Files & Directories
```
lupi-fy.com/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── render.yaml                        # Render deployment config
├── db.sqlite3                         # SQLite database
├── run_server.bat                     # Windows batch start script
├── run_server.ps1                     # PowerShell start script
├── daphne.log                         # WebSocket server logs
├── server.log                         # General server logs
│
├── mysite/                            # Django project settings
│   ├── settings.py                    # Global Django config
│   ├── urls.py                        # Main URL router
│   ├── wsgi.py                        # WSGI entry point
│   ├── asgi.py                        # ASGI entry point (Channels)
│   ├── routing.py                     # WebSocket routing
│   ├── views.py                       # Project-level views
│   └── __init__.py
│
├── accounts/                          # User auth & profiles
│   ├── models.py                      # CustomUser, UserProfile, etc.
│   ├── models_extended.py             # Extended models
│   ├── views.py                       # Auth views
│   ├── forms.py                       # User forms
│   ├── urls.py                        # Auth URLs
│   ├── admin.py                       # Admin panel config
│   ├── consumers.py                   # WebSocket consumers
│   ├── apps.py                        # App config
│   ├── tests.py                       # Unit tests
│   ├── utils.py                       # Helper functions
│   ├── migrations/                    # Database migrations
│   ├── management/                    # Custom management commands
│   ├── templates/accounts/            # Auth templates (13 files)
│   └── __init__.py
│
├── games/                             # Game creation & management
│   ├── models.py                      # Game, GameAsset, Score models
│   ├── views.py                       # Game views
│   ├── views_advanced.py              # Advanced game features
│   ├── urls.py                        # Game URLs
│   ├── admin.py                       # Admin config
│   ├── apps.py                        # App config
│   ├── tests.py                       # Game tests
│   ├── migrations/                    # Database migrations
│   └── __init__.py
│
├── core/                              # Core platform features
│   ├── models.py                      # Core models (currently empty)
│   ├── views.py                       # Core views (home, etc.)
│   ├── urls.py                        # Core URLs
│   ├── admin.py                       # Admin config
│   ├── apps.py                        # App config
│   ├── tests.py                       # Core tests
│   ├── migrations/                    # Database migrations
│   └── __init__.py
│
├── blog/                              # Blog & articles
│   ├── models.py                      # Blog post models
│   ├── views.py                       # Blog views
│   ├── urls.py                        # Blog URLs
│   ├── forms.py                       # Blog forms
│   ├── admin.py                       # Admin config
│   ├── apps.py                        # App config
│   ├── tests.py                       # Blog tests
│   ├── management/                    # Custom commands
│   ├── migrations/                    # Database migrations
│   ├── templates/blog/                # Blog templates (4 files)
│   └── __init__.py
│
├── communities/                       # Community management
│   ├── models.py                      # Community models
│   ├── views.py                       # Community views
│   ├── urls.py                        # Community URLs
│   ├── forms.py                       # Community forms
│   ├── admin.py                       # Admin config
│   ├── apps.py                        # App config
│   ├── tests.py                       # Community tests
│   ├── migrations/                    # Database migrations
│   ├── templates/communities/         # Community templates (4 files)
│   └── __init__.py
│
├── recommend/                         # Recommendation system
│   ├── models.py                      # Recommendation models
│   ├── views.py                       # Recommendation views
│   ├── urls.py                        # Recommendation URLs
│   ├── admin.py                       # Admin config
│   ├── apps.py                        # App config
│   ├── tests.py                       # Recommendation tests
│   ├── migrations/                    # Database migrations
│   └── __init__.py
│
├── chatbot/                           # AI Chatbot
│   ├── views.py                       # Chatbot views
│   ├── urls.py                        # Chatbot URLs
│   └── __init__.py
│
├── templates/                         # Global templates
│   ├── index.html                     # Home page
│   ├── dashboardhome.html             # Dashboard home
│   ├── search_results.html            # Search results
│   ├── lupiforge_guide.html           # Game creation guide
│   ├── terms.html                     # Terms of service
│   ├── auth_base.html                 # Auth base template
│   ├── games/                         # Game-specific templates (6 files)
│   ├── core/                          # Core templates (3 files)
│   └── chatbot/                       # Chatbot templates
│
├── static/                            # Static assets
│   ├── js/
│   │   ├── chatbot.js                 # Chatbot logic
│   │   ├── dashboard.js               # Dashboard interactivity
│   │   ├── game-execution-engine.js   # Game runtime engine
│   │   ├── websocket-fallback.js      # WebSocket backup
│   │   └── script.js                  # Global JS
│   ├── css/
│   │   ├── main.css                   # Main stylesheet
│   │   ├── chatbot.css                # Chatbot styles
│   │   ├── dashboard.css              # Dashboard styles
│   │   ├── dashboard-complete.css
│   │   ├── dashboard-fixes.css
│   │   ├── dashboard-inline.css
│   │   ├── search_results-inline.css
│   │   └── letter_set_game-inline.css
│   ├── style.css                      # Global style
│   └── svg/                           # SVG icons
│
├── media/                             # User-uploaded files
│   ├── avatars/                       # User profile pictures
│   ├── game_assets/                   # Game sprites, sounds, etc.
│   ├── game_thumbnails/               # Game preview images
│   └── thumbnails/                    # Asset thumbnails
│
├── staticfiles/                       # Collected static files (production)
│
├── avatars/                           # Avatar files
│
├── data/                              # Data files
│
├── scripts/                           # Utility scripts
│
├── tests/                             # Test files
│
├── .venv/                             # Virtual environment
│
├── .git/                              # Git repository
│
└── Documentation Files (*.md)         # 40+ markdown guides
    ├── README.md                      # Project readme
    ├── ARCHITECTURE.md                # System architecture
    ├── LUPIFORGE_USER_GUIDE.md        # Game creation guide
    ├── CHATBOT_QUICK_START.md         # Chatbot documentation
    ├── RECOMMENDATION_SYSTEM.md       # Recommendation logic
    ├── GOOGLE_OAUTH_SETUP.md          # OAuth configuration
    ├── DEPLOYMENT_CHECKLIST.md        # Deployment guide
    └── [30+ other documentation files]
```

---

## DJANGO APPS & MODELS

### 1. ACCOUNTS APP (User Authentication & Profiles)

**Location:** `accounts/`

#### Models
```
CustomUser (extends AbstractUser)
├── Fields:
│   ├── bio, avatar, color
│   ├── is_verified, is_premium
│   ├── is_email_verified, email_verification_code
│   ├── social_youtube, social_instagram, social_tiktok, social_twitch, social_github
│   ├── public_profile, allow_public_socials, allow_dms
│   ├── blocked_users (M2M to self)
│   ├── warning_count, suspended_until
│   ├── phone_number (with validation)
│   ├── followers (M2M to self)
│   ├── saved_communities (M2M to Community)
│   ├── theme_preference (light/dark/system)
│   ├── accent_color, font_size
│   └── Methods: subscribe_to_community(), follow_author()

UserProfile (extended user info)

Subscription (user subscriptions to communities/authors)

UserNotification (in-app notifications)

UserPreference (user settings)

FollowerRelationship (for tracking followers)
```

#### Views
- `views.py` - Registration, login, email verification, OAuth login
- User profile management, settings, appearance preferences
- Email verification flow with 6-digit codes
- Google OAuth integration

#### Templates (13 files in `templates/accounts/`)
- `login.html` - Login page
- `login_backup.html` - Backup login
- `register.html` - Registration form
- `register_styled.html` - Styled registration
- `account_dashboard.html` - User dashboard
- `creator_dashboard.html` - Creator-specific dashboard
- `public_profile.html` - Public user profile view
- `notifications.html` - Notification center
- `subscriptions.html` - Subscription management
- `appearance.html` - Theme & UI preferences
- `chat.html` - Direct messaging
- `verify_email.html` - Email verification
- `google_login.html` - OAuth login

#### Forms
- Email, password validation
- Registration forms
- Profile update forms

#### URLs
- `accounts/login/` - Login
- `accounts/register/` - Registration
- `accounts/logout/` - Logout
- `accounts/profile/<username>/` - Public profile
- `accounts/dashboard/` - User dashboard
- `accounts/settings/` - Account settings
- `accounts/verify-email/` - Email verification

---

### 2. GAMES APP (2D Game Creation Platform)

**Location:** `games/`

#### Models
```
Game (Game object)
├── Fields:
│   ├── id (UUID primary key)
│   ├── title, slug, description
│   ├── owner (FK to CustomUser)
│   ├── thumbnail (ImageField)
│   ├── visibility (draft/pending/public/private)
│   ├── monetization_enabled
│   ├── created_at, updated_at
│   └── Methods: __str__()

GameAsset (Sprites, sounds, backgrounds)
├── Fields:
│   ├── game (FK to Game)
│   ├── name, asset_type (sprite/sound/background/animation)
│   ├── file (FileField)
│   ├── thumbnail (ImageField)
│   ├── metadata (JSONField) - width, height, duration
│   ├── created_at
│   └── Unique: (game, name)

GameVersion (Version snapshots)
├── Fields:
│   ├── game (FK to Game)
│   ├── version_number
│   ├── logic_json (JSONField) - Blockly XML/JSON
│   ├── bundle_url (game executable)
│   ├── created_at
│   ├── is_published
│   └── Unique: (game, version_number)

Score (Player game scores)
├── Fields:
│   ├── game (FK to Game)
│   ├── player (FK to CustomUser, nullable)
│   ├── value (FloatField)
│   ├── metadata (JSONField)
│   └── created_at

GameReport (Content moderation)
├── Fields:
│   ├── game (FK to Game)
│   ├── reported_by (FK to CustomUser)
│   ├── reason, description
│   ├── status (pending/reviewing/resolved)
│   └── created_at
```

#### Views
- `views.py` - Game creation, editing, publishing
- `views_advanced.py` - Advanced features (multiplayer, moderation, etc.)
- Game listing and discovery
- Asset upload and management
- Leaderboard management
- Multiplayer session management

#### Templates (6 files in `templates/games/`)
- `editor.html` - Game editor with Blockly
- `editor_enhanced.html` - Enhanced editor version
- `dashboard.html` - Game dashboard
- `creator_dashboard.html` - Creator analytics
- `game_lobby.html` - Multiplayer lobby
- `moderation.html` - Content moderation
- `tutorial.html` - Game creation tutorial
- `multiplayer.html` - Multiplayer features
- `games_hub.html` - Game discovery hub

#### URLs
- `games/create/` - Create new game
- `games/<slug>/edit/` - Edit game
- `games/<slug>/` - Play game
- `games/` - Game list/discovery
- `games/api/save/` - Save game data
- `games/api/publish/` - Publish game
- `games/api/upload-asset/` - Upload game asset
- `games/leaderboard/` - Global leaderboard
- `games/moderation/` - Moderation queue

---

### 3. BLOG APP (Article Publishing)

**Location:** `blog/`

#### Models
```
BlogPost
├── Fields:
│   ├── title, slug, content (TextField/RichText)
│   ├── author (FK to CustomUser)
│   ├── category, tags
│   ├── featured_image (ImageField)
│   ├── excerpt
│   ├── is_published, published_at
│   ├── created_at, updated_at
│   ├── views_count, likes_count
│   └── Methods: get_absolute_url()

BlogCategory (Post categorization)

BlogComment (User comments on posts)
├── Fields:
│   ├── post (FK to BlogPost)
│   ├── author (FK to CustomUser)
│   ├── content
│   ├── created_at, updated_at
│   └── parent (self-FK for threading)

BlogLike (Post likes/reactions)
├── Fields:
│   ├── post (FK to BlogPost)
│   ├── user (FK to CustomUser)
│   └── created_at
```

#### Views
- Blog post CRUD (Create, Read, Update, Delete)
- Category browsing
- Search and filtering
- Comment management
- Like/reaction system
- Moderation dashboard

#### Templates (4 files in `templates/blog/`)
- `blog_list.html` - Blog post list
- `post_detail.html` - Individual post view
- `create_post.html` - Create/edit post
- `moderation_dashboard.html` - Moderate posts

#### URLs
- `posts/` - Blog list
- `posts/<slug>/` - Blog post detail
- `posts/create/` - Create post
- `posts/<slug>/edit/` - Edit post
- `posts/<slug>/delete/` - Delete post
- `posts/category/<slug>/` - Category view

---

### 4. COMMUNITIES APP (Social Communities)

**Location:** `communities/`

#### Models
```
Community
├── Fields:
│   ├── name, slug, description
│   ├── creator (FK to CustomUser)
│   ├── members (M2M to CustomUser)
│   ├── icon (ImageField)
│   ├── is_private
│   ├── created_at, updated_at
│   ├── members_count, posts_count
│   └── Methods: get_absolute_url()

CommunityPost (Posts in communities)
├── Fields:
│   ├── community (FK to Community)
│   ├── author (FK to CustomUser)
│   ├── title, content
│   ├── created_at, updated_at
│   ├── likes_count, comments_count
│   └── Methods: get_absolute_url()

CommunityComment (Comments on community posts)
├── Fields:
│   ├── post (FK to CommunityPost)
│   ├── author (FK to CustomUser)
│   ├── content
│   ├── created_at, updated_at
│   └── parent (self-FK for threading)

CommunityModerator (Moderator assignments)

CommunityReport (Report inappropriate content)
```

#### Views
- Community creation and management
- Post CRUD in communities
- Member management
- Moderation tools
- Community discovery

#### Templates (4 files in `templates/communities/`)
- `communities_list.html` - Community browser
- `community_detail.html` - Single community page
- `create_community.html` - Create community
- `create_community_post.html` - Create post in community
- `community_post_detail.html` - Post detail view

#### URLs
- `communities/` - Community list
- `communities/<slug>/` - Community detail
- `communities/create/` - Create community
- `communities/<slug>/posts/` - Community posts
- `communities/<slug>/settings/` - Community settings

---

### 5. RECOMMEND APP (Recommendation Engine)

**Location:** `recommend/`

#### Models
```
GameRecommendation
├── Fields:
│   ├── user (FK to CustomUser)
│   ├── game (FK to Game)
│   ├── score (FloatField) - recommendation strength
│   ├── reason (TextField) - why recommended
│   └── created_at

UserPreference (for recommendation tracking)
├── Fields:
│   ├── user (FK to CustomUser)
│   ├── game_type, difficulty_preference
│   └── interaction_count

RecommendationLog (analytics)
├── Fields:
│   ├── recommendation (FK)
│   ├── clicked, played
│   └── timestamp
```

#### Views
- Personalized game recommendations
- Recommendation API endpoints
- Trending games algorithm
- User preference learning

#### URLs
- `recommend/games/` - Get recommendations
- `recommend/trending/` - Trending games
- `recommend/api/feedback/` - Log interaction

---

### 6. CHATBOT APP (AI Assistant)

**Location:** `chatbot/`

#### Views
- Chatbot API endpoints
- Message processing
- AI response generation (via Ollama or external API)
- Chat history storage

#### Templates
- `templates/chatbot/index.html` - Chatbot UI

#### URLs
- `chatbot/send-message/` - Send chat message
- `chatbot/history/` - Get chat history

---

### 7. CORE APP (Core Platform Features)

**Location:** `core/`

#### Models
- Currently minimal (empty models.py)
- Can be expanded for core features

#### Views
- Home page
- Search functionality
- Global page elements

#### Templates (3 files in `templates/core/`)
- `letter_set_game.html` - Game example
- `letter_set_game_old.html` - Legacy version
- `game_lobby.html` - Game lobby

#### URLs
- `/` - Home page
- `/search/` - Search results

---

## HTML TEMPLATES (COMPLETE LIST)

### Total: 46+ HTML Templates

#### Root Level HTML (Temporary/Test Files)
- `blog_old.html` - Legacy blog template
- `subscriptions_old.html` - Legacy subscriptions
- `dashboard.html` - Standalone dashboard
- `dash_live.html` - Live dashboard view
- `response_editor_debug.html` - Debug response editor
- `response_editor_enhanced.html` - Enhanced editor

#### Main Templates (8 files in `templates/`)
```
templates/
├── index.html                    # Home page - 390 lines
├── dashboardhome.html            # Dashboard home
├── search_results.html           # Search interface
├── lupiforge_guide.html          # Game guide
├── terms.html                    # Terms of service
├── auth_base.html                # Auth base layout
├── games/                        (6 files)
├── core/                         (3 files)
└── chatbot/                      (1 file)
```

#### Accounts Templates (13 files)
```
accounts/templates/accounts/
├── login.html                    # Login interface
├── login_backup.html             # Backup login
├── register.html                 # Registration form
├── register_styled.html          # Styled registration
├── account_dashboard.html        # User dashboard
├── creator_dashboard.html        # Creator analytics
├── public_profile.html           # User profile view
├── notifications.html            # Notification center
├── subscriptions.html            # Manage subscriptions
├── appearance.html               # Theme settings
├── chat.html                     # DM interface
├── verify_email.html             # Email verification
└── google_login.html             # OAuth login
```

#### Games Templates (9 files)
```
games/templates/games/
├── editor.html                   # Game editor - 282 lines
├── editor_enhanced.html          # Enhanced editor
├── dashboard.html                # Game dashboard
├── creator_dashboard.html        # Creator dashboard
├── game_lobby.html               # Multiplayer lobby
├── moderation.html               # Content moderation
├── tutorial.html                 # Creation tutorial
├── multiplayer.html              # Multiplayer page
└── games_hub.html                # Game discovery
```

#### Blog Templates (4 files)
```
blog/templates/blog/
├── blog_list.html                # Post listing
├── post_detail.html              # Single post
├── create_post.html              # Create/edit post
└── moderation_dashboard.html     # Blog moderation
```

#### Communities Templates (5 files)
```
communities/templates/communities/
├── communities_list.html         # Community list
├── community_detail.html         # Single community
├── create_community.html         # Create community
├── create_community_post.html    # Create post
└── community_post_detail.html    # Post detail
```

#### Core Templates (3 files)
```
core/templates/core/
├── letter_set_game.html          # Game template
├── letter_set_game_old.html      # Legacy
└── game_lobby.html               # Game lobby
```

#### Chatbot Templates (1 file)
```
chatbot/templates/chatbot/
└── index.html                    # Chatbot interface
```

---

## URL ROUTING

### Main URL Configuration (`mysite/urls.py`)
```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("", include("core.urls")),
    path("posts/", include("blog.urls")),
    path("communities/", include("communities.urls")),
    path("games/", include("games.urls")),
    path("recommend/", include("recommend.urls")),
    path("chatbot/", include("chatbot.urls")),
]
```

### Accounts URLs (`accounts/urls.py`)
```
/accounts/login/
/accounts/register/
/accounts/logout/
/accounts/profile/<username>/
/accounts/dashboard/
/accounts/settings/
/accounts/verify-email/
/accounts/notifications/
/accounts/subscriptions/
```

### Games URLs (`games/urls.py`)
```
/games/
/games/create/
/games/<slug>/
/games/<slug>/edit/
/games/<slug>/delete/
/games/api/save/
/games/api/publish/
/games/api/upload-asset/
/games/api/delete-asset/
/games/leaderboard/
/games/moderation/
/games/<slug>/submit-score/
```

### Blog URLs (`blog/urls.py`)
```
/posts/
/posts/<slug>/
/posts/create/
/posts/<slug>/edit/
/posts/<slug>/delete/
/posts/category/<category>/
/posts/<slug>/comments/
```

### Communities URLs (`communities/urls.py`)
```
/communities/
/communities/create/
/communities/<slug>/
/communities/<slug>/posts/
/communities/<slug>/join/
/communities/<slug>/leave/
/communities/<slug>/settings/
```

### Core URLs (`core/urls.py`)
```
/
/search/
/dashboard/
/guide/
```

### Recommend URLs (`recommend/urls.py`)
```
/recommend/games/
/recommend/trending/
/recommend/api/feedback/
```

### Chatbot URLs (`chatbot/urls.py`)
```
/chatbot/send-message/
/chatbot/history/
```

---

## STATIC ASSETS

### JavaScript Files (`static/js/`)

#### 1. **game-execution-engine.js**
- Runtime engine for executing game logic
- Integrates Phaser 3D game framework
- Processes Blockly-generated JSON
- Handles game state, sprites, physics
- Event-driven architecture for game events

#### 2. **dashboard.js**
- Dashboard interactivity
- Chart rendering and updates
- Real-time metrics
- Click handlers and data fetching
- Theme switching logic

#### 3. **chatbot.js**
- Chatbot UI logic
- Message sending/receiving
- WebSocket integration
- UI state management
- Response parsing

#### 4. **websocket-fallback.js**
- WebSocket connection management
- Fallback to polling if WebSocket fails
- Reconnection logic
- Message queuing

#### 5. **script.js**
- Global page functionality
- Navigation
- Authentication checks
- Form submissions
- Theme persistence

### CSS Files (`static/css/`)

#### 1. **main.css**
- Global styles
- Typography system
- Color variables
- Responsive grid

#### 2. **style.css**
- Primary stylesheet
- Component styles
- Utility classes

#### 3. **dashboard.css**
- Dashboard layout styles
- Chart styling
- Responsive dashboard

#### 4. **dashboard-complete.css**
- Extended dashboard styles
- Animation definitions
- Advanced layouts

#### 5. **dashboard-fixes.css**
- Bug fixes and patches
- Additional responsive rules

#### 6. **dashboard-inline.css**
- Inline styles for dashboard

#### 7. **chatbot.css**
- Chatbot-specific styles
- Message bubble styling
- Input area styling

#### 8. **search_results-inline.css**
- Search results page styles

#### 9. **letter_set_game-inline.css**
- Game-specific styles

### SVG Icons (`static/svg/`)
- Icon assets for UI

---

## DATABASE SCHEMA

### High-Level Entity Relationship

```
CustomUser (Core Identity)
├── Profile relationship with UserProfile
├── Followers (Self M2M)
├── Saved Communities (M2M with Community)
├── Games Owned (FK to Game.owner)
├── Blog Posts (FK to BlogPost.author)
├── Community Memberships (M2M with Community)
├── Created Communities (FK to Community.creator)
├── Game Scores (FK to Score.player)
├── Notifications (FK to UserNotification.user)
└── Subscriptions (FK to Subscription.user)

Game (Game Object)
├── Owner (FK to CustomUser)
├── Assets (FK to GameAsset)
├── Versions (FK to GameVersion)
├── Scores (FK to Score)
└── Reports (FK to GameReport)

GameAsset (Game Files)
├── Game (FK)
└── Types: sprite, sound, background, animation

GameVersion (Game Snapshots)
├── Game (FK)
├── logic_json (Blockly blocks)
└── Multiple versions per game

Score (Leaderboard Entries)
├── Game (FK)
├── Player (FK to CustomUser, nullable)
└── Ranking computed from value

BlogPost (Article)
├── Author (FK to CustomUser)
├── Category (FK to BlogCategory)
├── Comments (FK to BlogComment)
├── Likes (FK to BlogLike)
└── Tags (M2M)

Community (Social Communities)
├── Creator (FK to CustomUser)
├── Members (M2M with CustomUser)
├── Posts (FK to CommunityPost)
├── Moderators (FK to CommunityModerator)
└── Reports (FK to CommunityReport)

Notification System
├── UserNotification (in-app messages)
├── UserPreference (notification settings)
└── Subscription (follow/subscribe tracking)
```

### Table Summary
| Table Name | Purpose | Key Fields |
|---|---|---|
| accounts_customuser | User accounts | username, email, avatar, profile |
| games_game | Game records | title, owner, visibility, created_at |
| games_gameasset | Game sprites/sounds | game, file, asset_type |
| games_gameversion | Version control | game, version_number, logic_json |
| games_score | Leaderboard | game, player, value |
| blog_blogpost | Articles | title, author, content, published_at |
| communities_community | Communities | name, creator, members |
| recommend_gamerecommendation | Recommendations | user, game, score |

---

## API ENDPOINTS

### Games API

**Save Game**
```
POST /games/api/save/
Body: {
  "title": "string",
  "description": "string",
  "logic_json": {...},
  "asset_ids": [...]
}
Response: { "game_id": "uuid", "success": true }
```

**Publish Game**
```
POST /games/api/publish/
Body: { "game_id": "uuid" }
Response: { "success": true, "message": "..." }
```

**Upload Asset**
```
POST /games/api/upload-asset/
Content-Type: multipart/form-data
Fields:
  - game_id (UUID)
  - file (binary)
  - name (string)
  - asset_type (sprite/sound/background)
Response: { "asset_id": "uuid", "url": "string" }
```

**Get Leaderboard**
```
GET /games/leaderboard/?game_id=<uuid>&limit=10
Response: {
  "scores": [
    {"rank": 1, "player": "username", "value": 1000, "date": "..."}
  ]
}
```

**Submit Score**
```
POST /games/<game_slug>/submit-score/
Body: { "value": 1000 }
Response: { "success": true, "rank": 5 }
```

### Recommendation API

**Get Recommendations**
```
GET /recommend/games/?limit=5
Response: {
  "recommendations": [
    {
      "game": {...},
      "score": 0.95,
      "reason": "Based on your interest in puzzle games"
    }
  ]
}
```

### Chatbot API

**Send Message**
```
POST /chatbot/send-message/
Body: { "message": "How do I create a game?" }
Response: {
  "message_id": "uuid",
  "response": "To create a game, click...",
  "timestamp": "2025-12-13T..."
}
```

**Get History**
```
GET /chatbot/history/?limit=50
Response: {
  "messages": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
  ]
}
```

---

## KEY FEATURES

### 1. Game Creation Platform
- **Blockly Editor**: Drag-and-drop visual programming
- **Phaser Integration**: 2D game runtime engine
- **Asset Manager**: Upload sprites, sounds, backgrounds
- **Live Preview**: See changes in real-time
- **Version Control**: Multiple game snapshots
- **Publishing Workflow**: Draft → Pending → Public

### 2. Multiplayer Gaming
- **WebSocket Support**: Real-time player sync
- **Game Lobbies**: Join multiplayer sessions
- **Leaderboards**: Global and per-game rankings
- **Score Submission**: Automatic tracking

### 3. Community System
- **Community Creation**: Users can create communities
- **Post System**: Community members post content
- **Moderation**: Flag and review inappropriate content
- **Member Management**: Join/leave communities

### 4. Blog Platform
- **Article Creation**: Rich text editing
- **Categories & Tags**: Organization
- **Comments**: User discussions
- **Likes/Reactions**: Engagement metrics
- **Search**: Find posts by title/content

### 5. User Authentication
- **Email/Password**: Traditional auth
- **Google OAuth**: Social login
- **Email Verification**: 6-digit codes
- **Profile Customization**: Avatar, bio, socials
- **Appearance Settings**: Light/dark theme, fonts

### 6. AI Chatbot
- **Game Help**: Assist users in creating games
- **General QA**: Answer platform questions
- **Ollama Integration**: On-device AI option
- **Chat History**: Conversation persistence

### 7. Recommendation Engine
- **Personalized Suggestions**: Based on play history
- **Trending Games**: Popular games algorithm
- **Genre-Based**: Match user preferences
- **Analytics**: Track recommendation success

### 8. Creator Dashboard
- **Game Analytics**: Views, plays, average score
- **Revenue Tracking**: Monetization metrics
- **Creator Leaderboard**: Top creators by revenue
- **Content Management**: Edit/delete games

---

## DEVELOPER GUIDE FOR AI

### How to Help with Code

When assisting with development, an AI should:

#### 1. **Understanding Game Logic**
The game engine processes Blockly-generated JSON. Key concept:
```javascript
// Example logic_json from Blockly
{
  "events": [
    {
      "type": "update",
      "actions": [
        {"type": "move_sprite", "sprite": "player", "x": 10},
        {"type": "check_collision", "sprite": "player", "target": "enemy"}
      ]
    }
  ]
}
```

#### 2. **Adding New Features**
To add new features:
1. **Create Model** in appropriate app: `models.py`
2. **Create View/API** in `views.py`
3. **Create Template** in `templates/appname/`
4. **Add URL Route** in `urls.py`
5. **Create Migrations**: `python manage.py makemigrations`
6. **Add Static Assets** if needed in `static/`

#### 3. **Working with WebSockets**
- WebSocket consumers in `accounts/consumers.py`
- Routing in `mysite/routing.py`
- Uses Channels library (4.1.0)

#### 4. **File Locations by Feature**

| Feature | Location |
|---------|----------|
| User Auth | accounts/views.py, accounts/models.py |
| Games | games/views.py, games/models.py, templates/games/ |
| Blog | blog/views.py, blog/models.py, templates/blog/ |
| Communities | communities/views.py, communities/models.py |
| Recommendations | recommend/views.py, recommend/models.py |
| Chatbot | chatbot/views.py, chatbot/urls.py |
| Global | mysite/urls.py, templates/index.html |

#### 5. **Common Tasks**

**Adding a New Game Block Type:**
1. Modify `game-execution-engine.js` to handle new block
2. Update Game model if tracking new data
3. Add corresponding Blockly block definition

**Creating a New Page:**
1. Add view in appropriate `views.py`
2. Create `.html` template
3. Add URL route
4. Add navigation link in layout

**Adding Database Field:**
1. Add field to model in `models.py`
2. Create migration: `python manage.py makemigrations`
3. Apply migration: `python manage.py migrate`
4. Update admin.py if needed

#### 6. **Testing**
- Unit tests in `tests.py` files
- Run: `python manage.py test`
- Functional tests in `tests/` directory

#### 7. **Key Technologies to Know**
- **Backend**: Django 4.2.27, Channels 4.1.0
- **Frontend**: Vanilla JS, Blockly 11.3.0, Phaser 3.60.0
- **Styling**: Tailwind CSS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: django-allauth (OAuth support)
- **WebSockets**: Channels + Daphne server

#### 8. **Deployment**
- Hosted on Render.com
- Uses render.yaml configuration
- Gunicorn for WSGI
- Daphne for ASGI (WebSockets)
- WhiteNoise for static files

### Common Code Patterns

**Django View with Authentication:**
```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def my_view(request):
    user_profile = request.user
    context = {'user': user_profile}
    return render(request, 'template.html', context)
```

**API Response:**
```python
from django.http import JsonResponse

def api_endpoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Process
        return JsonResponse({'success': True, 'data': {...}})
```

**Template with Context:**
```html
<h1>Welcome, {{ user.username }}</h1>
{% if user.is_authenticated %}
  <p>User profile: {{ user.profile.role }}</p>
{% endif %}
```

---

## QUICK REFERENCE TABLE

| Component | Location | Purpose |
|-----------|----------|---------|
| Models | `[app]/models.py` | Database schema |
| Views | `[app]/views.py` | Business logic, HTTP responses |
| Templates | `templates/[app]/` | HTML pages |
| URLs | `[app]/urls.py` | Route configuration |
| Forms | `[app]/forms.py` | User input handling |
| Admin | `[app]/admin.py` | Django admin panel |
| Tests | `[app]/tests.py` | Unit tests |
| Static CSS | `static/css/` | Stylesheets |
| Static JS | `static/js/` | JavaScript files |
| Migrations | `[app]/migrations/` | Database changes |
| Settings | `mysite/settings.py` | Project configuration |
| Main URLs | `mysite/urls.py` | Main routing |

---

## DOCUMENTATION FILES

The project includes 40+ markdown documentation files for reference:
- ARCHITECTURE.md - System design
- LUPIFORGE_USER_GUIDE.md - User guide for game creation
- CHATBOT_QUICK_START.md - Chatbot documentation
- RECOMMENDATION_SYSTEM.md - Recommendation algorithm
- DEPLOYMENT_CHECKLIST.md - Deployment procedures
- And many more...

All are located in the root directory.

---

## CONCLUSION

This comprehensive report provides everything needed for AI-assisted development of the Lupi-fy platform. The app is a full-featured game creation, community, and blogging platform built with Django, featuring a Blockly-based game editor, WebSocket support for real-time features, and a modular architecture for easy expansion.

For questions about specific features or code locations, refer to this guide and the documentation files in the root directory.

**Last Updated:** December 13, 2025  
**Project Status:** Active Development

