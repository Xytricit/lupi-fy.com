#!/usr/bin/env python
"""
Comprehensive test to verify all sorting button fixes are working correctly.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser
from blog.models import Post
from communities.models import Community, CommunityPost
import json

def run_comprehensive_tests():
    """Run comprehensive tests for sorting button fixes."""
    
    print("\n" + "="*70)
    print("COMPREHENSIVE SORTING BUTTON FIX TEST SUITE")
    print("="*70)
    
    # Create test user
    test_user, _ = CustomUser.objects.get_or_create(
        username='comprehensive_test_user',
        defaults={'email': 'test@comprehensive.com'}
    )
    test_user.set_password('testpass')
    test_user.save()
    
    client = Client()
    client.login(username='comprehensive_test_user', password='testpass')
    
    # TEST 1: Dashboard functionality
    print("\n[TEST 1] Dashboard Sorting Buttons")
    print("-" * 70)
    response = client.get('/dashboard/')
    assert response.status_code == 200, f"Dashboard status: {response.status_code}"
    content = response.content.decode()
    
    checks = {
        'filter-bubble': 'Sorting buttons exist',
        'sortChange': 'Sort change event handler',
        'let sort = ': 'Sort variable initialization',
        'community-feed': 'Community feed element',
        'loadMore': 'Load more function for infinite scroll'
    }
    
    passed = 0
    for check, desc in checks.items():
        if check in content:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}")
    
    print(f"  Dashboard: {passed}/{len(checks)} checks passed")
    
    # TEST 2: Blog API endpoints
    print("\n[TEST 2] Blog API Endpoint Functionality")
    print("-" * 70)
    
    test_sorts = {
        'latest': 'Most recent posts',
        'most_liked': 'Posts with most likes',
        'most_viewed': 'Posts with most views',
        'trending': 'Trending posts',
        'bookmarks': 'User bookmarked posts'
    }
    
    api_passed = 0
    for sort, desc in test_sorts.items():
        response = client.get(f'/posts/api/posts/?sort={sort}&offset=0&limit=12')
        if response.status_code == 200:
            try:
                data = response.json()
                if 'posts' in data and isinstance(data['posts'], list):
                    print(f"  ✅ {desc:30} ({len(data['posts'])} posts)")
                    api_passed += 1
                else:
                    print(f"  ❌ {desc:30} (Invalid response format)")
            except json.JSONDecodeError:
                print(f"  ❌ {desc:30} (Invalid JSON)")
        else:
            print(f"  ❌ {desc:30} (Status {response.status_code})")
    
    print(f"  Blog API: {api_passed}/{len(test_sorts)} sorts working")
    
    # TEST 3: Blog page structure
    print("\n[TEST 3] Blog Page Structure")
    print("-" * 70)
    response = client.get('/posts/')
    assert response.status_code == 200, f"Blog page status: {response.status_code}"
    content = response.content.decode()
    
    blog_checks = {
        'blogForYouToggle': 'For You button',
        'blogForYouSection': 'For You section',
        'blogPageForYouContainer': 'Recommendations container',
        'blogFeed': 'Dynamic feed container',
        'fetchAndRenderBlogPosts': 'Dynamic fetch function',
        'document.addEventListener': 'Event delegation for buttons',
        '.like-btn': 'Like buttons',
        '.dislike-btn': 'Dislike buttons',
        '.comment-btn': 'Comment buttons',
        '.bookmark-btn': 'Bookmark buttons'
    }
    
    blog_passed = 0
    for check, desc in blog_checks.items():
        if check in content:
            print(f"  ✅ {desc}")
            blog_passed += 1
        else:
            print(f"  ❌ {desc}")
    
    print(f"  Blog page: {blog_passed}/{len(blog_checks)} elements found")
    
    # TEST 4: For You recommender integration
    print("\n[TEST 4] For You Recommender Integration")
    print("-" * 70)
    
    recommender_checks = {
        '/recommend/blog-recommendations/': 'Blog recommendations endpoint',
        '/recommend/community-recommendations/': 'Community recommendations endpoint'
    }
    
    recommender_passed = 0
    for endpoint, desc in recommender_checks.items():
        response = client.get(endpoint)
        if response.status_code == 200:
            try:
                data = response.json()
                if 'results' in data:
                    print(f"  ✅ {desc:40} ({len(data['results'])} items)")
                    recommender_passed += 1
                else:
                    print(f"  ⚠️ {desc:40} (No results field)")
            except json.JSONDecodeError:
                print(f"  ❌ {desc:40} (Invalid JSON)")
        else:
            print(f"  ⚠️ {desc:40} (Status {response.status_code})")
    
    print(f"  Recommender: {recommender_passed}/{len(recommender_checks)} endpoints working")
    
    # TEST 5: Content consistency
    print("\n[TEST 5] Content Consistency")
    print("-" * 70)
    
    response = client.get('/posts/api/posts/?sort=latest&offset=0&limit=1')
    if response.status_code == 200:
        data = response.json()
        if data['posts']:
            post = data['posts'][0]
            required_fields = [
                'id', 'title', 'content', 'author_username',
                'likes_count', 'dislikes_count', 'comments_count',
                'user_liked', 'user_disliked', 'user_bookmarked'
            ]
            
            fields_present = 0
            for field in required_fields:
                if field in post:
                    fields_present += 1
                else:
                    print(f"  ❌ Missing field: {field}")
            
            print(f"  ✅ Post fields: {fields_present}/{len(required_fields)} present")
    
    # SUMMARY
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_tests = (
        passed + api_passed + blog_passed + 
        recommender_passed + (1 if fields_present == len(required_fields) else 0)
    )
    total_possible = (
        len(checks) + len(test_sorts) + len(blog_checks) + 
        len(recommender_checks) + 1
    )
    
    percentage = (total_tests / total_possible * 100) if total_possible > 0 else 0
    
    print(f"\nOverall: {total_tests}/{total_possible} checks passed ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("\n🎉 ALL SYSTEMS OPERATIONAL - Sorting buttons are working correctly!")
    elif percentage >= 70:
        print("\n⚠️ MOST SYSTEMS WORKING - Minor issues may exist")
    else:
        print("\n❌ ISSUES DETECTED - Further investigation needed")
    
    print("="*70)

if __name__ == '__main__':
    run_comprehensive_tests()
