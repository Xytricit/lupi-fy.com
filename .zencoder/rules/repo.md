---
description: Repository Information Overview
alwaysApply: true
---

# LupiForge - Game Platform Information

## Summary

LupiForge (lupi-fy.com) is a comprehensive Django-based web platform for creating, sharing, and playing interactive games. The platform features a marketplace for game distribution, community systems, blog functionality, and AI-powered recommendation engine using machine learning.

## Repository Structure

### Main Directories

- **accounts/**: User authentication, profiles, subscriptions, and social features (followers/following)
- **games/**: Game creation, storage, and execution engine with advanced view handling
- **marketplace/**: Game marketplace with project management and distribution
- **recommend/**: ML-based recommendation system with hybrid torch models
- **blog/**: User-generated blog posts with commenting and moderation
- **communities/**: Community creation, management, and community-specific posts
- **chatbot/**: AI chatbot integration for user assistance
- **core/**: Core application views and general routing
- **mysite/**: Django project configuration and main settings
- **static/**: CSS, JavaScript, and SVG assets
- **templates/**: HTML templates for all app modules
- **media/**: User-uploaded files (avatars, game thumbnails, post images, etc.)
- **tests/**: Integration and UI test suites

## Language & Runtime

**Language**: Python  
**Version**: Python 3.11 (specified in render.yaml)  
**Framework**: Django 5.2.8  
**Build System**: pip + Django management commands  
**Package Manager**: pip

## Dependencies

**Core Framework**:
- Django 5.2.8
- channels 4.1.0 (WebSocket support)
- django-allauth 0.60+ (OAuth and authentication)

**Web & Server**:
- gunicorn 23.0.0
- asgiref 3.11.0
- whitenoise 6.11.0 (static file serving)
- websockets 11.0.3

**Authentication & Security**:
- PyJWT 2.8+
- cryptography 41+
- beautifulsoup4 4.12.2

**Data & Files**:
- Pillow 10+ (image processing)
- sqlparse 0.5.4
- requests 2.31+

**Machine Learning**:
- torch (used in recommend app via torch_recommender models)

**Utilities**:
- packaging 25.0
- tzdata 2025.2

## Build & Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

**Development Server**:
```bash
python manage.py runserver
```

**Production Server** (Render.com):
```bash
gunicorn mysite.wsgi:application
```

## Testing

**Framework**: Django's built-in test framework + custom test files  
**Test Locations**: 
- `tests/` directory (integration and UI tests)
- Individual app test files: `{app}/tests.py`

**Test Files**:
- `test_subscriptions_integration.py` - Subscription feature tests
- `test_subscriptions_buttons.py` - UI button tests
- `test_editor_initialization.py` - Game editor initialization
- `test_dashboard_fixes.py` - Dashboard functionality
- `test_ui_comprehensive.py` - Comprehensive UI tests

**Run Command**:
```bash
python manage.py test
```

## Main Components

### Entry Points

- **manage.py**: Django management CLI
- **mysite/wsgi.py**: WSGI application for production servers
- **mysite/asgi.py**: ASGI application with WebSocket support (Channels)

### Database

**Engine**: SQLite (development)  
**Configuration**: `mysite/settings.py`  
**Migrations**: Located in each app's `migrations/` directory  
**Custom User Model**: `accounts.CustomUser`

### Authentication

**System**: Django Allauth + Google OAuth  
**Features**:
- Email/username login
- Google OAuth2 integration
- Social account linking
- Account verification optional for social login

### WebSocket & Real-time

**Framework**: Django Channels  
**Configuration**: `mysite/routing.py` and `mysite/asgi.py`  
**Channel Layer**: In-memory (development)

### Static & Media Files

**Static Files**: Served by WhiteNoise in production  
**Media Root**: `media/` directory  
**Endpoints**: 
- `/static/` - Static assets
- `/media/` - User-uploaded files

## Configuration Files

- **mysite/settings.py**: Main Django configuration
- **mysite/urls.py**: URL routing
- **mysite/asgi.py**: ASGI configuration with Channels
- **render.yaml**: Render.com deployment configuration

## Management Commands

Custom management commands available in `{app}/management/commands/`:

- `train_creator_bot.py` - Train creator bot model
- `setup_google_oauth.py` - Configure Google OAuth
- `train_torch_recs.py` - Train recommendation model
- `seed_interactions.py` - Seed user interaction data
- `compute_recommendations.py` - Compute recommendations

## Key Features Implemented

- **Game Creation & Editor**: Enhanced HTML editor for game design
- **Marketplace**: Browse, upload, and download games
- **Recommendations**: Hybrid ML-based recommendation engine
- **Communities**: User communities with posts and discussions
- **Blog**: Full blog platform with comments and moderation
- **Chatbot**: AI-powered user assistance
- **Real-time**: WebSocket support via Channels
- **Subscriptions**: User subscription management
- **Social Features**: Follow/follower system, social profiles
