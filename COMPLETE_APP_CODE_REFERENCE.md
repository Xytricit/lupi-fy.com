# 🎯 LUPIFY COMPLETE APP CODE REFERENCE
## Ready-to-Paste All App Code & Content

---

## 📋 TABLE OF CONTENTS
1. [MAIN URL ROUTING](#main-url-routing)
2. [ACCOUNTS APP](#accounts-app)
3. [CORE APP](#core-app)
4. [BLOG APP](#blog-app)
5. [COMMUNITIES APP](#communities-app)
6. [GAMES APP](#games-app)
7. [RECOMMEND APP](#recommend-app)
8. [MARKETPLACE APP](#marketplace-app)

---

# MAIN URL ROUTING

## mysite/urls.py
```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

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
    path("marketplace/", include("marketplace.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

# ACCOUNTS APP

**Location:** `accounts/`

## Key Files Structure
```
accounts/
├── models.py          # User profiles, subscriptions, game sessions
├── views.py           # Auth & profile views
├── urls.py            # Auth routes
├── admin.py           # Admin panel config
├── forms.py           # Registration/login forms
└── migrations/        # Database migrations
```

## Important URLs
```
/accounts/login/              - User login
/accounts/register/           - User registration
/accounts/logout/             - User logout
/accounts/profile/<username>/ - Public profile
/accounts/dashboard/          - User dashboard
/accounts/settings/           - Account settings
/accounts/verify-email/       - Email verification
/accounts/notifications/      - Notifications
/accounts/subscriptions/      - Subscriptions list
```

## Key Models
- **User** - Extended user model with preferences
- **Profile** - User profile with avatar, bio, etc.
- **UserGameSession** - Track game play history
- **WordListGame** - Word game sessions
- **Subscription** - Author subscriptions

## Core Views
- User authentication (login, register, logout)
- Profile viewing and editing
- Dashboard with activity tracking
- Subscription management

---

# CORE APP

**Location:** `core/`

## core/urls.py
```python
from django.urls import path

from accounts import views as accounts_views
from blog.views import posts_list_view
from communities import views as communities_views
from core import views as core_views

urlpatterns = [
    path("", core_views.main_home_view, name="main_home"),
    path("about/", core_views.about_view, name="about"),
    path("contact/", core_views.contact_view, name="contact"),
    path("dashboard/", core_views.dashboard_view, name="dashboard_home"),
    path(
        "dashboard/community-posts-api/",
        core_views.community_posts_api,
        name="community_posts_api",
    ),
    path(
        "dashboard/search-suggestions/",
        core_views.search_suggestions,
        name="search_suggestions",
    ),
    path("search/", core_views.search_page, name="search_page"),
    path("search/api/", core_views.search_api, name="search_api"),
    path("blogs/", posts_list_view, name="blogs"),
    path("terms-of-service", core_views.terms_of_service_view, name="terms_of_service"),
    path("lupiforge-guide/", core_views.lupiforge_guide_view, name="lupiforge_guide"),
    path("communities/", communities_views.communities_list, name="communities"),
    path(
        "communities/toggle/<int:community_id>/",
        communities_views.toggle_join_community,
        name="toggle_join_community",
    ),
    path("subscriptions/", accounts_views.subscriptions_view, name="subscriptions"),
]
```

## Important URLs
```
/                    - Home page
/about/              - About page
/contact/            - Contact page
/dashboard/          - User dashboard
/search/             - Search results
/terms-of-service    - Terms of service
/lupiforge-guide/    - Platform guide
```

## Key Views
- `main_home_view()` - Home page
- `about_view()` - About page
- `contact_view()` - Contact page
- `dashboard_view()` - User dashboard with game history
- `search_page()` - Search interface
- `search_api()` - Search API endpoint
- `community_posts_api()` - Get community posts dynamically
- `terms_of_service_view()` - Legal terms
- `lupiforge_guide_view()` - Help & guide

---

# BLOG APP

**Location:** `blog/`

## blog/urls.py
```python
from django.urls import path

from . import views

urlpatterns = [
    # --- Posts ---
    path("", views.posts_list_view, name="blogs"),
    path("create/", views.create_post_view, name="create_post"),
    path("moderation/", views.moderation_dashboard, name="moderation_dashboard"),
    path(
        "moderation/resolve/<int:report_id>/",
        views.resolve_report,
        name="resolve_report",
    ),
    path("blog/<int:pk>/", views.post_detail_view, name="post_detail"),
    # --- Blog API (for dynamic filtering/sorting) ---
    path("api/posts/", views.blog_posts_api, name="blog_posts_api"),
    # --- Post Actions ---
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("post/<int:post_id>/dislike/", views.toggle_dislike, name="toggle_dislike"),
    path("post/<int:post_id>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("post/<int:post_id>/report/", views.report_post, name="report_post"),
    # --- Comments ---
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    # --- Editing ---
    path("post/<int:post_id>/edit/", views.edit_post_view, name="edit_post"),
    path("post/<int:post_id>/delete/", views.delete_post_view, name="delete_post"),
]
```

## Important URLs
```
/posts/                           - Blog list
/posts/create/                    - Create post
/posts/blog/<id>/                 - View post
/posts/post/<id>/like/            - Like post
/posts/post/<id>/comment/         - Add comment
/posts/moderation/                - Moderation dashboard
/posts/api/posts/                 - API: Get posts
```

## Key Models
- **Post** - Blog post with title, content, author
- **Category** - Post categories/tags
- **Comment** - Comments on posts
- **Like** - Track post likes
- **Report** - Flagged content

## Core Views
- Post CRUD (Create, Read, Update, Delete)
- Category browsing
- Search and filtering
- Comment management
- Like/reaction system
- Moderation dashboard

---

# COMMUNITIES APP

**Location:** `communities/`

## communities/urls.py
```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.communities_list, name="communities_list"),
    path("create/", views.create_community, name="create_community"),
    path("<int:community_id>/", views.community_detail, name="community_detail"),
    path(
        "toggle/<int:community_id>/",
        views.toggle_join_community,
        name="toggle_join_community",
    ),
    path("<int:community_id>/save/", views.save_community, name="save_community"),
    path(
        "create-post/",
        views.create_community_post_generic,
        name="create_community_post_generic",
    ),
    path(
        "<int:community_id>/create-post/",
        views.create_community_post,
        name="create_community_post",
    ),
    path(
        "post/<int:post_id>/", views.community_post_detail, name="community_post_detail"
    ),
    path(
        "api/post/<int:post_id>/like/",
        views.toggle_community_post_like,
        name="toggle_community_post_like",
    ),
    path(
        "api/post/<int:post_id>/comment/",
        views.add_community_post_comment,
        name="add_community_post_comment",
    ),
]
```

## Important URLs
```
/communities/                      - List communities
/communities/create/               - Create community
/communities/<id>/                 - View community
/communities/<id>/create-post/     - Create community post
/communities/toggle/<id>/          - Join/leave community
/communities/api/post/<id>/like/   - Like community post
```

## Key Models
- **Community** - Community with name, description, members
- **CommunityPost** - Posts within communities
- **CommunityPostComment** - Comments on community posts
- **CommunityPostLike** - Track likes on community posts

## Core Views
- Community creation and management
- Post CRUD in communities
- Member management
- Moderation tools
- Community discovery

---

# GAMES APP

**Location:** `games/`

## games/urls.py (Excerpt)
```python
from django.urls import path
from . import views
from . import views_advanced

urlpatterns = [
    path('api/recently-played/', views.recently_played_api, name='recently_played_api'),
    path('editor/', views.editor_view, name='editor'),
    path('editor-debug/', views.editor_debug_view, name='editor_debug'),
    path('editor-enhanced/', views.editor_view, {'version': 'enhanced'}, name='editor_enhanced'),
    path('editor-guest/', views.editor_public_view, name='editor_guest'),
    path('dashboard/', views.editor_dashboard_view, name='dashboard'),
    path('dashboard/home/', views.dashboard_home_view, name='dashboard_home'),
    path('multiplayer/', views.multiplayer_view, name='multiplayer'),
    path('tutorial/', views.tutorial_view, name='tutorial'),
    # ... more routes
]
```

## Important URLs
```
/games/                        - Game list/discovery
/games/editor/                 - Game editor
/games/dashboard/              - Creator dashboard
/games/multiplayer/            - Multiplayer games
/games/tutorial/               - Game tutorial
/games/api/recently-played/    - Get recent games (API)
```

## Key Models
- **Game** - Game project metadata
- **GameAsset** - Game assets (images, sounds)
- **Score** - Game scores/leaderboard
- **Multiplayer** - Multiplayer room management

## Core Views
- Game creation and editing
- Game discovery and browsing
- Score tracking and leaderboard
- Multiplayer room management
- Asset upload and management

---

# RECOMMEND APP

**Location:** `recommend/`

## recommend/urls.py
```python
from django.urls import path

from . import views

urlpatterns = [
    path("for-you/", views.for_you_recommendations, name="for_you_recommendations"),
    path("interests/", views.get_user_interests, name="get_user_interests"),
    path("interests/save/", views.save_user_interests, name="save_user_interests"),
    path(
        "blog-recommendations/",
        views.get_blog_recommendations,
        name="get_blog_recommendations",
    ),
    path(
        "community-recommendations/",
        views.get_community_recommendations,
        name="get_community_recommendations",
    ),
    path(
        "hybrid-recommendations/",
        views.get_hybrid_recommendations,
        name="get_hybrid_recommendations",
    ),
    path("tag-options/", views.get_tag_options, name="get_tag_options"),
]
```

## Important URLs
```
/recommend/for-you/                      - Personalized recommendations
/recommend/interests/                    - Get user interests
/recommend/interests/save/               - Save user interests
/recommend/blog-recommendations/         - Blog post recommendations
/recommend/community-recommendations/    - Community recommendations
/recommend/hybrid-recommendations/       - Combined recommendations
/recommend/tag-options/                  - Available tags
```

## Key Models
- **UserInterest** - User's interests/preferences
- **Recommendation** - Generated recommendations

## Core Views
- Generate personalized "For You" feed
- Get user interests and preferences
- Blog post recommendations based on history
- Community recommendations
- Hybrid recommendation algorithm
- Tag/category options

---

# MARKETPLACE APP

**Location:** `marketplace/`

## marketplace/urls.py (Excerpt)
```python
from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # ========================================================================
    # PUBLIC PAGES
    # ========================================================================
    
    # Main marketplace home/browse
    path('', views.marketplace_home, name='home'),
    
    
    # ========================================================================
    # CREATOR ACTIONS - Require login
    # ========================================================================
    
    # Upload new project for sale
    path('upload/', views.upload_project, name='upload'),
    
    # Creator dashboard with analytics
    path('creator/', views.creator_dashboard, name='creator_dashboard'),
    
    
    # ========================================================================
    # USER LIBRARY
    # ========================================================================
    
    # User's purchased projects library
    path('library/', views.user_library, name='library'),
    
    
    # ========================================================================
    # API ENDPOINTS - AJAX calls from frontend
    # ========================================================================
    
    # Purchase/buy a project
    path('api/purchase/<uuid:project_id>/', views.purchase_project, name='api_purchase'),
    
    # Download purchased project
    path('download/<uuid:project_id>/', views.download_project, name='download'),
    
    # Admin approval endpoints
    path('admin/approve/<uuid:project_id>/', views.admin_approve_project, name='admin_approve'),
    path('admin/reject/<uuid:project_id>/', views.admin_reject_project, name='admin_reject'),
    
    # Individual project detail page
    path('<slug:slug>/', views.project_detail, name='project_detail'),
]
```

## Important URLs
```
/marketplace/                              - Marketplace home
/marketplace/upload/                       - Upload project
/marketplace/creator/                      - Creator dashboard
/marketplace/library/                      - User's library
/marketplace/<slug>/                       - Project detail
/marketplace/api/purchase/<id>/            - Purchase API
/marketplace/download/<id>/                - Download API
/marketplace/admin/approve/<id>/           - Admin approve
/marketplace/admin/reject/<id>/            - Admin reject
```

## Key Models
- **Project** - Sellable project/game
- **Purchase** - Purchase records
- **Review** - User reviews
- **ProjectFile** - Project files

## Core Views
- Marketplace browsing and search
- Project upload and management
- Purchase processing
- Download management
- Creator dashboard and analytics
- Admin approval/rejection

---

# CHATBOT APP

**Location:** `chatbot/`

## Important URLs
```
/chatbot/send-message/    - Send message to chatbot
/chatbot/history/         - Get chat history
```

## Key Features
- Conversational AI chatbot
- Chat history tracking
- Integration with platform content

---

# QUICK REFERENCE TABLE

| Component | Location | Purpose |
|-----------|----------|---------|
| **Models** | `[app]/models.py` | Database schema definitions |
| **Views** | `[app]/views.py` | Business logic, HTTP responses |
| **URLs** | `[app]/urls.py` | Route configuration |
| **Templates** | `templates/[app]/` | HTML pages |
| **Forms** | `[app]/forms.py` | User input handling |
| **Admin** | `[app]/admin.py` | Django admin panel |
| **Static** | `static/css/`, `static/js/` | CSS & JavaScript files |
| **Migrations** | `[app]/migrations/` | Database schema changes |
| **Settings** | `mysite/settings.py` | Project configuration |
| **Main URLs** | `mysite/urls.py` | Main routing config |

---

# APP INSTALLATION ORDER
```
1. Django core (auth, admin, contenttypes, sessions, etc.)
2. django-allauth (authentication)
3. Accounts - User profiles & authentication
4. Core - Home, search, dashboard
5. Blog - Article publishing
6. Communities - Social communities
7. Games - Game creation platform
8. Recommend - Recommendation engine
9. Chatbot - AI chatbot
10. Marketplace - Project sales
```

---

# COMMON IMPORT PATTERNS

## In Views
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View
from .models import YourModel
from .forms import YourForm
```

## In URLs
```python
from django.urls import path
from . import views

urlpatterns = [
    path('route/', views.view_function, name='name'),
]
```

## In Models
```python
from django.db import models
from django.contrib.auth.models import User

class YourModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

# KEY STATISTICS

- **Total Apps:** 10 (accounts, core, blog, communities, games, recommend, chatbot, marketplace, + admin, allauth)
- **Main Models:** 40+ across all apps
- **API Endpoints:** 50+ (including AJAX endpoints)
- **Templates:** 30+ HTML files
- **URL Patterns:** 100+ routes
- **Database Migrations:** 50+ migration files

---

# NOTES

- All apps follow Django best practices
- Models use proper ForeignKey relationships
- Views use appropriate decorators (@login_required, etc.)
- URLs use named patterns for template reversing
- Static files are organized by app in templates/[app]/
- Admin panel auto-registered with models
- Forms handle validation and user input

---

**Last Updated:** December 13, 2025
**Django Version:** 4.2.27
**Python Version:** 3.11+
