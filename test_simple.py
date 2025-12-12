import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

c = Client()
c.force_login(user)
resp = c.get('/dashboard/')
content = resp.content.decode()

# Simple string checks
print(f"Page contains create-btn: {'create-btn' in content}")
print(f"Page contains createModal: {'createModal' in content}")
print(f"Page contains blog-post: {'blog-post' in content}")
print(f"Page contains community-post: {'community-post' in content}")

# Check if JavaScript function is there
print(f"Page contains initCreateModal: {'initCreateModal' in content}")

# Look for the actual event listener code
print(f"Page contains addEventListener: {'addEventListener' in content}")

# Find the positions
if 'create-btn' in content:
    idx = content.find('create-btn')
    print(f"\ncreate-btn found at position {idx}")
    print(f"Context: {content[max(0,idx-50):idx+100]}")

if 'initCreateModal' in content:
    idx = content.find('initCreateModal')
    print(f"\ninitCreateModal found at position {idx}")
    print(f"Context: {content[idx:idx+200]}")
