import json
import os
import sys

import django  # noqa: E402

# Ensure project root is on sys.path so 'mysite' package is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.test import Client  # noqa: E402

User = get_user_model()
username = "__testuser__"
password = "testpass123"
user = User.objects.filter(username=username).first()
if not user:
    user = User.objects.create_user(
        username=username, password=password, email="test@test.local"
    )
    user.save()

client = Client()
logged = client.login(username=username, password=password)
print("logged in:", logged)
resp = client.post(
    "/accounts/api/game/post-message/",
    json.dumps({"content": "hello from debug_post"}),
    content_type="application/json",
)
print("status", resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.content)
