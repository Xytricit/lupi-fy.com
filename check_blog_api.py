#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser
from blog.models import Post
import json

client = Client()

# Create test user
user, _ = CustomUser.objects.get_or_create(
    username='testblogapi',
    defaults={'email': 'test@blogapi.com'}
)
user.set_password('testpass')
user.save()

# Login
client.login(username='testblogapi', password='testpass')

# Test blog API
print("Testing blog API endpoints...")

sorts = ['latest', 'most_liked', 'most_viewed', 'trending', 'bookmarks']
for sort in sorts:
    response = client.get(f'/posts/api/posts/?sort={sort}&offset=0&limit=12')
    print(f"Sort={sort:15} | Status: {response.status_code}", end=" ")
    
    if response.status_code == 200:
        try:
            data = response.json()
            if 'posts' in data and 'total' in data:
                print(f"| Posts: {len(data['posts'])}")
            else:
                print("| Missing fields in response")
        except json.JSONDecodeError:
            print("| Invalid JSON")
    else:
        print(f"| Error")

# Test blog page
print("\nTesting blog page...")
response = client.get('/posts/')
if response.status_code == 200:
    content = response.content.decode()
    
    # Check for required elements
    checks = {
        'blogForYouToggle': 'For You button',
        'blogForYouSection': 'For You section',
        'blogPageForYouContainer': 'Recommendations container',
        'blogFeed': 'Feed container',
        'fetchAndRenderBlogPosts': 'API fetch function',
        'document.addEventListener': 'Event delegation'
    }
    
    for key, desc in checks.items():
        if key in content:
            print(f"  ✅ {desc}")
        else:
            print(f"  ❌ {desc} not found")
else:
    print(f"Cannot access blog page - got {response.status_code}")
