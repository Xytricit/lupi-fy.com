import os
import django
from django.test import Client
import traceback
import sys

# Ensure project root is on sys.path so `mysite` can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

client = Client()

routes = [
    '/',
    '/admin/',
    '/accounts/register/',
    '/accounts/login/',
    '/accounts/dashboard/',
    '/accounts/profile/',
    '/accounts/subscriptions/',
    '/accounts/account/',
    '/dashboard/',
    '/blogs/',
    '/posts/',
    '/posts/create/',
    '/posts/moderation/',
    '/communities/',
]

results = []
for path in routes:
    try:
        resp = client.get(path)
        results.append((path, resp.status_code, resp.url if resp.status_code in (301,302) else None, None))
    except Exception as e:
        tb = traceback.format_exc()
        results.append((path, 'EXCEPTION', None, tb))

for r in results:
    p, status, redirect, tb = r
    if status == 'EXCEPTION':
        print(f"{p}: EXCEPTION\n{tb}\n")
    else:
        print(f"{p}: HTTP {status} redirect={redirect}")
