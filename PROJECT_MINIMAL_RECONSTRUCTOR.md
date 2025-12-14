# Minimal Project Reconstructor

Purpose: a very small, focused single-file blueprint an AI (or a human) can use to recreate the project structure and exact core files needed to run the app locally.

How to use: create a new repo, then create the files below with exact contents. Run the setup commands at the end.

---

## Files included (minimal, exact content blocks follow)
- `manage.py`
- `requirements.txt`
- `mysite/settings.py`
- `mysite/urls.py`
- `mysite/asgi.py`
- `mysite/wsgi.py`
- `core/apps.py`, `core/models.py`, `core/views.py`, `core/urls.py`, `core/admin.py`, `core/__init__.py`
- `accounts/apps.py`, `accounts/models.py`, `accounts/urls.py` (minimal stubs)
- `blog/apps.py`, `blog/models.py`, `blog/urls.py` (minimal stubs)
- `templates/base.html` (minimal template)
- `static/css/main.css` (placeholder)

All other apps can be scaffolded with the same patterns.

---

## Exact file contents (copy-paste)

### manage.py
```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

---

### requirements.txt
```
Django>=4.2,<5
psycopg2-binary==2.9.10
gunicorn
```

---

### mysite/__init__.py
(leave file empty)

---

### mysite/settings.py
```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'replace-with-secure-key'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core',
    'accounts',
    'blog',
    # add other apps: games, communities, recommend, marketplace, chatbot
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]},
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

### mysite/urls.py
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
]
```

---

### mysite/asgi.py
```python
import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
application = get_asgi_application()
```

---

### mysite/wsgi.py
```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
application = get_wsgi_application()
```

---

### core/__init__.py
(leave empty)

---

### core/apps.py
```python
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
```

---

### core/models.py
```python
from django.db import models

class HealthCheck(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=200, blank=True)
```

---

### core/views.py
```python
from django.shortcuts import render

def home(request):
    return render(request, 'base.html')
```

---

### core/urls.py
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
```

---

### core/admin.py
```python
from django.contrib import admin
from .models import HealthCheck

admin.site.register(HealthCheck)
```

---

### accounts/apps.py
```python
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'accounts'
```
```

---

### accounts/models.py
```python
from django.db import models

# Minimal user extension sample
class Profile(models.Model):
    user_id = models.IntegerField()
    display_name = models.CharField(max_length=100, blank=True)
```
```

---

### accounts/urls.py
```python
from django.urls import path
from django.http import HttpResponse

urlpatterns = [
    path('', lambda r: HttpResponse('Accounts root')),
]
```

---

### blog/apps.py
```python
from django.apps import AppConfig

class BlogConfig(AppConfig):
    name = 'blog'
```
```

---

### blog/models.py
```python
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
```
```

---

### blog/urls.py
```python
from django.urls import path
from django.http import HttpResponse

urlpatterns = [
    path('', lambda r: HttpResponse('Blog root')),
]
```
```

---

### templates/base.html
```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Lupify (minimal)</title>
    <link rel="stylesheet" href="/static/css/main.css">
  </head>
  <body>
    <header><h1>Site</h1></header>
    <main>{% block content %}{% endblock %}</main>
  </body>
</html>
```

---

### static/css/main.css
```css
body { font-family: sans-serif; margin: 0; padding: 1rem; }
header { background: #222; color: white; padding: 1rem; }
```

---

## Quick recreate commands
Run these after creating files:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Notes for an AI that will recreate the full project
- The document contains exact minimal implementations of the key files. An AI can generate the remaining apps (`games`, `communities`, `recommend`, `marketplace`, `chatbot`) by copying the `blog` or `accounts` pattern and restoring full models/views from the original `PROJECT_ESSENTIAL_FILES.md` if needed.
- Keep `INSTALLED_APPS` ordered: Django contrib apps first, then local apps.
- Use this minimal repo as a working seed; expand by adding the fuller app code when required.

---

File written: `PROJECT_MINIMAL_RECONSTRUCTOR.md`
