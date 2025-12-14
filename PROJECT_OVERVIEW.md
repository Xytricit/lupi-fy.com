# Project Overview

## Project Description
[Edit this section with your project description]

This is a Python/Django project that contains multiple modules for handling various functionalities.

## Project Statistics

- **Total Source Files**: 19941
- **Entry Points**: 69

## Folder Structure

\`\`\`
├── accounts
│   ├── management
│   │   ├── commands
│   │   └── __init__.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_customuser_color_alter_customuser_bio.py
│   │   ├── 0003_customuser_suspended_until_customuser_warning_count_and_more.py
│   │   ├── 0004_subscription.py
│   │   ├── 0005_alter_subscription_options_and_more.py
│   │   ├── 0006_customuser_public_profile_customuser_social_github_and_more.py
│   │   ├── 0007_customuser_followers.py
│   │   ├── 0008_alter_subscription_community.py
│   │   ├── 0009_customuser_saved_communities.py
│   │   └── 0010_add_allow_public_socials.py
│   │       ... and 17 more files
│   ├── templates
│   │   └── accounts
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── forms.py
│   ├── models.py
│   ├── models_extended.py
│   ├── tests.py
│   ├── urls.py
│   └── utils.py
│       ... and 1 more files
├── avatars
│   ├── Nana_avatar.png
│   ├── Nana_avatar_7XgJCIY.png
│   ├── Nana_avatar_Mge3Jiv.png
│   ├── Nana_avatar_oBSIF9s.png
│   ├── Nana_avatar_PKBThsp.png
│   ├── Nana_avatar_U8xCh0z.png
│   ├── Screenshot_2025-12-05_144629.png
│   └── Screenshot_2025-12-05_144629_2oAqQ8R.png
├── blog
│   ├── management
│   │   └── commands
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_comment_dislikes_comment_likes.py
│   │   ├── 0003_remove_comment_dislikes_remove_comment_likes_and_more.py
│   │   ├── 0004_remove_post_followers.py
│   │   ├── 0005_comment_parent.py
│   │   ├── 0006_moderationreport_post.py
│   │   ├── 0007_add_post_views.py
│   │   └── __init__.py
│   ├── templates
│   │   └── blog
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── chatbot
│   ├── urls.py
│   └── views.py
├── claude_chunks
│   ├── _venv_chunk1.txt
│   ├── _venv_Lib_site-packages__distutils_hack_chunk1.txt
│   ├── _venv_Lib_site-packages_allauth_account_chunk1.txt
│   ├── _venv_Lib_site-packages_allauth_account_chunk2.txt
│   ├── _venv_Lib_site-packages_allauth_account_internal_chunk1.txt
│   ├── _venv_Lib_site-packages_allauth_account_internal_flows_chunk1.txt
│   ├── _venv_Lib_site-packages_allauth_account_management_chunk1.txt
│   ├── _venv_Lib_site-packages_allauth_account_management_commands_chunk1.txt
│   ├── _venv_Lib_site-packages_allauth_account_migrations_chunk1.txt
│   └── _venv_Lib_site-packages_allauth_account_static_account_js_chunk1.txt
│       ... and 2472 more files
├── communities
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_alter_community_options_communitypost.py
│   │   ├── 0003_community_banner_image_community_community_image_and_more.py
│   │   ├── 0004_communitypost_image.py
│   │   ├── 0005_communitypost_bookmarks_communitypost_dislikes_and_more.py
│   │   ├── 0006_communitypostcomment_moderationreport.py
│   │   └── __init__.py
│   ├── templates
│   │   └── communities
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── core
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_delete_community.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── data
│   └── recommend
│       ├── torch_recommender.pt
│       └── torch_recommender_hybrid.pt
├── games
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_game_thumbnail.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── views_advanced.py
├── marketplace
│   ├── management
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── media
│   ├── avatars
│   │   ├── __testuser___avatar_6.png
│   │   ├── baconboy_avatar.png
│   │   ├── nana_akwasi_avatar_5.png
│   │   ├── Nana_avatar.png
│   │   ├── Nana_avatar_0qzwIKX.png
│   │   ├── NANA_avatar_2.png
│   │   ├── Nana_avatar_3.png
│   │   ├── Nana_avatar_3cTxri5.png
│   │   ├── nana_avatar_4.png
│   │   └── Nana_avatar_DpOgTY3.png
│   │       ... and 10 more files
│   ├── community_banners
│   │   ├── create_community_banner.png
│   │   └── dogs_banner.png
│   ├── community_images
│   │   ├── create_community_logo.png
│   │   └── dogs_logo.png
│   ├── game_thumbnails
│   │   └── 2025
│   ├── marketplace
│   │   ├── projects
│   │   └── thumbnails
│   ├── post_images
│   │   ├── chosostunned.jpg
│   │   ├── dog.jpeg
│   │   └── trojan.jpg
│   └── posts
│       ├── chosostunned.jpeg
│       ├── chosostunned.jpg
│       ├── chosostunned_u50IXe3.jpeg
│       ├── dog.jpeg
│       ├── Icons_Set.png
│       ├── resized_lupify_image_600px.jpg
│       ├── trojan.jpeg
│       └── trojan.jpg
├── mysite
│   ├── __init__.py
│   ├── asgi.py
│   ├── routing.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── recommend
│   ├── management
│   │   └── commands
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_userinterests.py
│   │   ├── 0003_rename_categories_userinterests_blog_tags_and_more.py
│   │   └── __init__.py
│   ├── ml
│   │   ├── torch_recommender.py
│   │   └── torch_recommender_hybrid.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── scripts
│   ├── check_post.py
│   ├── check_routes.py
│   ├── debug_post.py
│   ├── fetch_debug.py
│   ├── fetch_editor.py
│   ├── fetch_wordlist.py
│   ├── report_test.py
│   └── verify_template_urls.py
├── static
│   ├── css
│   │   ├── chatbot.css
│   │   ├── dashboard-complete.css
│   │   ├── dashboard-fixes.css
│   │   ├── dashboard-inline.css
│   │   ├── dashboard.css
│   │   ├── letter_set_game-inline.css
│   │   ├── main.css
│   │   └── search_results-inline.css
│   ├── js
│   │   ├── chatbot.js
│   │   ├── dashboard.js
│   │   ├── game-execution-engine.js
│   │   └── websocket-fallback.js
│   ├── svg
│   │   └── game-controller.svg
│   ├── script.js
│   └── style.css
├── staticfiles
│   ├── admin
│   │   ├── css
│   │   ├── img
│   │   └── js
│   ├── script.js
│   └── style.css
├── templates
│   ├── chatbot
│   │   └── index.html
│   ├── core
│   │   ├── game_lobby.html
│   │   ├── games_hub.html
│   │   ├── letter_set_game.html
│   │   └── letter_set_game_old.html
│   ├── games
│   │   ├── creator_dashboard.html
│   │   ├── dashboard.html
│   │   ├── editor.html
│   │   ├── editor_enhanced.html
│   │   ├── moderation.html
│   │   ├── multiplayer.html
│   │   └── tutorial.html
│   ├── marketplace
│   │   ├── creator_dashboard.html
│   │   ├── home.html
│   │   ├── index.html
│   │   ├── library.html
│   │   ├── project_detail.html
│   │   └── upload.html
│   ├── auth_base.html
│   ├── base.html
│   ├── dashboardhome.html
│   ├── index.html
│   ├── lupiforge_guide.html
│   ├── search_results.html
│   └── terms.html
├── tests
│   ├── test_subscriptions_buttons.py
│   └── test_subscriptions_integration.py
├── .gitignore
├── .tmp_test_ollama.py
├── AI_ADMIN_COMMANDS_GUIDE.md
├── APP_COMPLETE_REPORT.md
├── ARCHITECTURE.md
├── AUTH_STYLING_GUIDE.md
├── AVATAR_AND_CREATE_CHECKLIST.md
├── BACKEND_INTEGRATION_GUIDE.md
├── blog_old.html
└── build_essential_package.py
    ... and 100 more files
\`\`\`

## Entry Points

Entry points detected:

- `.venv/Lib/site-packages/PIL/__main__.py`
- `.venv/Lib/site-packages/allauth/idp/oidc/internal/oauthlib/server.py`
- `.venv/Lib/site-packages/asgiref/server.py`
- `.venv/Lib/site-packages/asgiref/wsgi.py`
- `.venv/Lib/site-packages/autobahn/__main__.py`
- `.venv/Lib/site-packages/black/__main__.py`
- `.venv/Lib/site-packages/blackd/__main__.py`
- `.venv/Lib/site-packages/certifi/__main__.py`
- `.venv/Lib/site-packages/charset_normalizer/__main__.py`
- `.venv/Lib/site-packages/charset_normalizer/cli/__main__.py`
- `.venv/Lib/site-packages/daphne/__main__.py`
- `.venv/Lib/site-packages/daphne/cli.py`
- `.venv/Lib/site-packages/daphne/server.py`
- `.venv/Lib/site-packages/django/__main__.py`
- `.venv/Lib/site-packages/django/contrib/admin/views/main.py`
- `.venv/Lib/site-packages/django/core/asgi.py`
- `.venv/Lib/site-packages/django/core/handlers/asgi.py`
- `.venv/Lib/site-packages/django/core/handlers/wsgi.py`
- `.venv/Lib/site-packages/django/core/wsgi.py`
- `.venv/Lib/site-packages/dotenv/__main__.py`
- `.venv/Lib/site-packages/dotenv/cli.py`
- `.venv/Lib/site-packages/dotenv/main.py`
- `.venv/Lib/site-packages/flake8/__main__.py`
- `.venv/Lib/site-packages/flake8/main/cli.py`
- `.venv/Lib/site-packages/gunicorn/__main__.py`
- `.venv/Lib/site-packages/gunicorn/http/wsgi.py`
- `.venv/Lib/site-packages/isort/__main__.py`
- `.venv/Lib/site-packages/isort/main.py`
- `.venv/Lib/site-packages/numpy/f2py/__main__.py`
- `.venv/Lib/site-packages/pip/__main__.py`
- `.venv/Lib/site-packages/pip/_internal/cli/main.py`
- `.venv/Lib/site-packages/pip/_internal/commands/index.py`
- `.venv/Lib/site-packages/pip/_internal/main.py`
- `.venv/Lib/site-packages/pip/_internal/models/index.py`
- `.venv/Lib/site-packages/pip/_vendor/certifi/__main__.py`
- `.venv/Lib/site-packages/pip/_vendor/dependency_groups/__main__.py`
- `.venv/Lib/site-packages/pip/_vendor/distro/__main__.py`
- `.venv/Lib/site-packages/pip/_vendor/platformdirs/__main__.py`
- `.venv/Lib/site-packages/pip/_vendor/pygments/__main__.py`
- `.venv/Lib/site-packages/pip/_vendor/rich/__main__.py`
- `.venv/Lib/site-packages/platformdirs/__main__.py`
- `.venv/Lib/site-packages/pyflakes/__main__.py`
- `.venv/Lib/site-packages/pytokens/__main__.py`
- `.venv/Lib/site-packages/pytokens/cli.py`
- `.venv/Lib/site-packages/setuptools/_vendor/backports/tarfile/__main__.py`
- `.venv/Lib/site-packages/setuptools/_vendor/platformdirs/__main__.py`
- `.venv/Lib/site-packages/setuptools/_vendor/wheel/__main__.py`
- `.venv/Lib/site-packages/sqlparse/__main__.py`
- `.venv/Lib/site-packages/sqlparse/cli.py`
- `.venv/Lib/site-packages/torch/_inductor/compile_worker/__main__.py`
- `.venv/Lib/site-packages/torch/distributed/run.py`
- `.venv/Lib/site-packages/torch/utils/bottleneck/__main__.py`
- `.venv/Lib/site-packages/torch/utils/model_dump/__main__.py`
- `.venv/Lib/site-packages/twisted/__main__.py`
- `.venv/Lib/site-packages/twisted/application/app.py`
- `.venv/Lib/site-packages/twisted/internet/main.py`
- `.venv/Lib/site-packages/twisted/names/server.py`
- `.venv/Lib/site-packages/twisted/trial/__main__.py`
- `.venv/Lib/site-packages/twisted/web/server.py`
- `.venv/Lib/site-packages/twisted/web/wsgi.py`
- `.venv/Lib/site-packages/ubjson/__main__.py`
- `.venv/Lib/site-packages/websockets/__main__.py`
- `.venv/Lib/site-packages/websockets/legacy/server.py`
- `.venv/Lib/site-packages/websockets/server.py`
- `.venv/Lib/site-packages/websockets/sync/server.py`
- `.venv/Lib/site-packages/wheel/__main__.py`
- `manage.py`
- `mysite/asgi.py`
- `mysite/wsgi.py`

## Coding Rules & Guidelines

[Edit this section with your coding standards]

### Python Standards
- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions and classes
- Maximum line length: 88 characters (Black formatter)

### Testing
- All new features must include tests
- Maintain test coverage above 80%
- Use pytest for testing

### Version Control
- Commit messages should be descriptive
- Use feature branches
- Keep commits atomic and logical

## How to Use with Claude AI

1. Start with this overview file
2. Upload chunks incrementally to Claude
3. Reference specific file groups and modules
4. Use the claude_chunks/MANIFEST.md for organization

## Next Steps

- [ ] Review and customize this overview
- [ ] Upload chunks to Claude in order
- [ ] Reference specific files when discussing features
- [ ] Update with project-specific information
