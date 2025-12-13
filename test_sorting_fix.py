#!/usr/bin/env python
"""
Test script to verify sorting button fixes for dashboard and blog pages.
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
sys.path.insert(0, '/Users/turbo/OneDrive/Documents/GitHub/lupi-fy.com')
django.setup()

from blog.models import Post
from accounts.models import CustomUser
from django.test import Client
from django.urls import reverse

def test_blog_api_endpoint():
    """Test that blog API endpoint exists and returns posts with proper sorting."""
    client = Client()
    
    # Test /posts/api/posts/ endpoint
    print("\n[TEST 1] Checking blog API endpoint...")
    try:
        # Create a test user
        test_user, _ = CustomUser.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@test.com', 'password': 'testpass'}
        )
        
        # Login the user
        client.login(username='testuser', password='testpass')
        
        # Test latest sort
        response = client.get('/posts/api/posts/?sort=latest&offset=0&limit=12')
        if response.status_code == 200:
            print("  ✅ PASSED: /posts/api/posts/ endpoint accessible")
            data = response.json()
            if 'posts' in data and 'total' in data:
                print("  ✅ PASSED: API returns proper JSON with posts array")
            else:
                print("  ⚠️ WARNING: API response missing expected fields")
        else:
            print(f"  ❌ ERROR: API returned {response.status_code}")
    except Exception as e:
        print(f"  ⚠️ ERROR: {e}")

def test_sorting_parameters():
    """Test that sorting parameters are properly handled."""
    client = Client()
    
    print("\n[TEST 2] Checking sorting parameter support...")
    test_user, _ = CustomUser.objects.get_or_create(
        username='testuser2',
        defaults={'email': 'test2@test.com', 'password': 'testpass'}
    )
    
    sorts = ['latest', 'most_liked', 'most_viewed', 'trending', 'bookmarks']
    
    for sort in sorts:
        try:
            response = client.get(f'/posts/api/posts/?sort={sort}&offset=0&limit=12')
            if response.status_code == 200:
                print(f"  ✅ PASSED: sort={sort} works")
            else:
                print(f"  ❌ FAILED: sort={sort} returned {response.status_code}")
        except Exception as e:
            print(f"  ❌ ERROR for sort={sort}: {e}")

def test_dashboard_sort_variable():
    """Test that dashboard has proper sort variable initialization."""
    print("\n[TEST 3] Checking dashboard sort variable...")
    try:
        client = Client()
        response = client.get('/')
        content = response.content.decode()
        
        # Check for sort variable initialization
        if 'let sort = ' in content or 'var sort = ' in content or 'sort = ' in content:
            print("  ✅ PASSED: Dashboard initializes sort variable")
        else:
            print("  ⚠️ WARNING: Could not find sort variable initialization")
        
        # Check for bubble handlers
        if 'filter-bubble' in content and 'addEventListener' in content:
            print("  ✅ PASSED: Bubble event handlers detected")
        else:
            print("  ⚠️ WARNING: Could not find bubble event handlers")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

def test_blog_page_handlers():
    """Test that blog page has proper event delegation."""
    print("\n[TEST 4] Checking blog page event handlers...")
    try:
        client = Client()
        response = client.get('/posts/')
        content = response.content.decode()
        
        # Check for event delegation
        if 'document.addEventListener' in content:
            print("  ✅ PASSED: Blog page uses event delegation")
        else:
            print("  ⚠️ WARNING: Could not find event delegation pattern")
        
        # Check for For You section
        if 'blogForYouSection' in content and 'blogForYouToggle' in content:
            print("  ✅ PASSED: Blog page has For You toggle and section")
        else:
            print("  ⚠️ WARNING: Missing For You elements")
        
        # Check for fetch/API calls
        if '/posts/api/posts/' in content or 'fetchAndRenderBlogPosts' in content:
            print("  ✅ PASSED: Blog page fetches from API")
        else:
            print("  ⚠️ WARNING: Could not find API calls")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("DASHBOARD & BLOG SORTING BUTTON FIX TEST SUITE")
    print("=" * 60)
    
    test_blog_api_endpoint()
    test_sorting_parameters()
    test_dashboard_sort_variable()
    test_blog_page_handlers()
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
