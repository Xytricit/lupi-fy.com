#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

client = Client()

# Create test user
user, _ = CustomUser.objects.get_or_create(
    username='testdashboard',
    defaults={'email': 'test@dashboard.com'}
)
user.set_password('testpass')
user.save()

# Login
client.login(username='testdashboard', password='testpass')

# Check dashboard
response = client.get('/dashboard/')
print(f"Dashboard status: {response.status_code}")

if response.status_code == 200:
    content = response.content.decode()
    
    # Check for sort variable
    if 'let sort = ' in content or "let sort=" in content:
        print("✅ Found: let sort = ")
    elif 'var sort = ' in content or "var sort=" in content:
        print("✅ Found: var sort = ")
    else:
        # Look for it in the community posts section
        if 'sort =' in content:
            print("✅ Found sort variable (with spaces)")
        else:
            print("❌ No sort variable declaration found")
    
    # Check for sortChange event
    if 'sortChange' in content:
        print("✅ Found: sortChange event")
    else:
        print("❌ sortChange event not found")
    
    # Check filter-bubble
    if 'filter-bubble' in content:
        print("✅ Found: filter-bubble elements")
    else:
        print("❌ No filter-bubble elements")
        
    # Check community-feed
    if 'community-feed' in content:
        print("✅ Found: community-feed element")
    else:
        print("❌ No community-feed element")
        
    # Check for the infinite scroll setup
    if 'offset' in content and 'limit' in content:
        print("✅ Found: offset/limit pagination logic")
    else:
        print("❌ No pagination logic found")
else:
    print(f"Cannot access dashboard - got {response.status_code}")
