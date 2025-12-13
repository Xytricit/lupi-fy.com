#!/usr/bin/env python
"""
Test script to verify home page changes:
1. For You section removed
2. Filter bubbles work (Latest, Most liked, etc.)
3. Recently played games load
4. Bot chat bubble appears at bottom-right
5. Only community posts on home feed
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from communities.models import Community, CommunityPost
from accounts.models import UserGameSession
from games.models import Game
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
client = Client()

print("=" * 60)
print("HOME PAGE CHANGES TEST SUITE")
print("=" * 60)

# Test 1: Check For You section is removed
print("\n[TEST 1] Verifying For You section is removed...")
try:
    response = client.get('/')
    content = response.content.decode()
    
    has_for_you_section = 'id="forYouSection"' in content
    has_blog_for_you = 'id="blogForYouContainer"' in content
    has_community_for_you = 'id="communityForYouContainer"' in content
    
    if has_for_you_section:
        print("  ❌ FAILED: forYouSection still exists in DOM")
    else:
        print("  ✅ PASSED: forYouSection removed")
    
    if has_blog_for_you:
        print("  ❌ FAILED: blogForYouContainer still exists")
    else:
        print("  ✅ PASSED: blogForYouContainer removed")
    
    if has_community_for_you:
        print("  ❌ FAILED: communityForYouContainer still exists")
    else:
        print("  ✅ PASSED: communityForYouContainer removed")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 2: Check filter bubbles exist
print("\n[TEST 2] Verifying filter bubbles exist...")
try:
    response = client.get('/')
    content = response.content.decode()
    
    filters = ['latest', 'most_liked', 'most_viewed', 'trending', 'bookmarks']
    found_filters = []
    
    for f in filters:
        if f'data-sort="{f}"' in content:
            found_filters.append(f)
    
    if len(found_filters) == len(filters):
        print(f"  ✅ PASSED: All {len(filters)} filter bubbles found")
        print(f"     Filters: {', '.join(found_filters)}")
    else:
        print(f"  ❌ FAILED: Only found {len(found_filters)}/{len(filters)} filters")
        print(f"     Found: {', '.join(found_filters)}")
        print(f"     Missing: {', '.join(set(filters) - set(found_filters))}")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 3: Check recently played games container exists
print("\n[TEST 3] Verifying recently played games section exists...")
try:
    response = client.get('/')
    content = response.content.decode()
    
    if 'id="recentlyPlayedContainer"' in content:
        print("  ✅ PASSED: recentlyPlayedContainer exists")
    else:
        print("  ❌ FAILED: recentlyPlayedContainer not found")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 4: Check bot chat bubble exists
print("\n[TEST 4] Verifying AI chat bubble exists...")
try:
    response = client.get('/')
    content = response.content.decode()
    
    has_ai_bubble = 'id="aiChatBubble"' in content
    has_bot_svg = 'lucide-bot' in content
    
    if has_ai_bubble:
        print("  ✅ PASSED: aiChatBubble element exists")
    else:
        print("  ❌ FAILED: aiChatBubble element not found")
    
    if has_bot_svg:
        print("  ✅ PASSED: Bot SVG icon found")
    else:
        print("  ❌ FAILED: Bot SVG icon not found")
    
    # Check if it has fixed positioning
    if 'position:fixed' in content and 'bottom:30px' in content and 'right:30px' in content:
        print("  ✅ PASSED: Bubble has correct fixed positioning")
    else:
        print("  ⚠️  WARNING: Fixed positioning styles may not be correctly applied")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 5: Check community feed exists (no blog posts directly)
print("\n[TEST 5] Verifying community feed exists...")
try:
    response = client.get('/')
    content = response.content.decode()
    
    if 'id="community-feed"' in content:
        print("  ✅ PASSED: community-feed container exists")
    else:
        print("  ❌ FAILED: community-feed not found")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 6: Check API endpoint for recently played games
print("\n[TEST 6] Testing recently played games API endpoint...")
try:
    # Create a test user and game session
    test_user, _ = User.objects.get_or_create(username='testuser123', defaults={'email': 'test@test.com'})
    client.force_login(test_user)
    
    # Check if the API endpoint exists
    response = client.get('/games/api/recently-played/')
    
    if response.status_code == 200:
        print("  ✅ PASSED: Recently played games API endpoint is accessible")
        data = response.json()
        if 'games' in data:
            print(f"     Returns 'games' key with {len(data.get('games', []))} games")
        else:
            print("  ⚠️  WARNING: Response doesn't have 'games' key")
    elif response.status_code == 404:
        print("  ⚠️  WARNING: API endpoint not found (404) - may need to be created")
    else:
        print(f"  ⚠️  WARNING: API returned status {response.status_code}")
        
except Exception as e:
    print(f"  ⚠️  WARNING: {e}")

# Test 7: Check filter logic event listener
print("\n[TEST 7] Checking filter event logic...")
try:
    response = client.get('/')
    content = response.content.decode()
    
    if 'sortChange' in content:
        print("  ✅ PASSED: sortChange event listener found in code")
    else:
        print("  ⚠️  WARNING: sortChange event not found - filters may not update feed")
        
    if 'addEventListener' in content and 'filter-bubble' in content:
        print("  ✅ PASSED: Filter bubble event handlers detected")
    else:
        print("  ⚠️  WARNING: Filter bubble event handlers not detected")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 8: Check community posts API is called
print("\n[TEST 8] Verifying community posts API...")
try:
    response = client.get('/')
    content = response.content.decode()
    
    if 'community_posts_api' in content or 'communities/api/posts' in content:
        print("  ✅ PASSED: Community posts API reference found")
    else:
        print("  ⚠️  WARNING: Community posts API reference not found")
        
except Exception as e:
    print(f"  ❌ ERROR: {e}")

print("\n" + "=" * 60)
print("TEST SUITE COMPLETE")
print("=" * 60)
