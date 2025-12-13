"""
Comprehensive Testing Suite for lupi-fy.com
Tests all endpoints and features of the application
"""

import os
import sys
import django
import requests
from django.test import Client
from django.contrib.auth.models import User
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from accounts.models import Profile, Message, Notification
from blog.models import Post, Follow, PostReport
from communities.models import Community, CommunityPost, CommunityPostLike
from recommend.models import UserInterest

BASE_URL = "http://127.0.0.1:8000"

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []
        
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"✓ PASS: {test_name}")
        
    def add_fail(self, test_name, reason):
        self.failed.append((test_name, reason))
        print(f"✗ FAIL: {test_name} - {reason}")
        
    def add_error(self, test_name, error):
        self.errors.append((test_name, error))
        print(f"⚠ ERROR: {test_name} - {error}")
        
    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.errors)
        print("\n" + "="*80)
        print(f"TEST SUMMARY: {len(self.passed)}/{total} passed")
        print("="*80)
        if self.failed:
            print("\nFailed Tests:")
            for test, reason in self.failed:
                print(f"  - {test}: {reason}")
        if self.errors:
            print("\nError Tests:")
            for test, error in self.errors:
                print(f"  - {test}: {error}")

results = TestResults()
client = Client()

# ============================================================================
# 1. MAIN PAGES TESTS
# ============================================================================
print("\n\n" + "="*80)
print("1. TESTING MAIN PAGES")
print("="*80)

def test_main_home():
    """Test main home page"""
    try:
        response = client.get('/')
        if response.status_code == 200:
            results.add_pass("GET / (Main Home)")
        else:
            results.add_fail("GET / (Main Home)", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET / (Main Home)", str(e))

def test_dashboard():
    """Test dashboard page"""
    try:
        response = client.get('/dashboard/')
        if response.status_code in [200, 302]:  # 302 if redirecting to login
            results.add_pass("GET /dashboard/")
        else:
            results.add_fail("GET /dashboard/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /dashboard/", str(e))

def test_blogs_page():
    """Test blogs list page"""
    try:
        response = client.get('/blogs/')
        if response.status_code == 200:
            results.add_pass("GET /blogs/ (Blog List)")
        else:
            results.add_fail("GET /blogs/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /blogs/", str(e))

def test_communities_page():
    """Test communities list page"""
    try:
        response = client.get('/communities/')
        if response.status_code == 200:
            results.add_pass("GET /communities/")
        else:
            results.add_fail("GET /communities/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /communities/", str(e))

def test_search_page():
    """Test search page"""
    try:
        response = client.get('/search/')
        if response.status_code == 200:
            results.add_pass("GET /search/")
        else:
            results.add_fail("GET /search/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /search/", str(e))

def test_terms_of_service():
    """Test terms of service page"""
    try:
        response = client.get('/terms-of-service')
        if response.status_code == 200:
            results.add_pass("GET /terms-of-service")
        else:
            results.add_fail("GET /terms-of-service", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /terms-of-service", str(e))

# Run main page tests
test_main_home()
test_dashboard()
test_blogs_page()
test_communities_page()
test_search_page()
test_terms_of_service()

# ============================================================================
# 2. AUTHENTICATION TESTS
# ============================================================================
print("\n\n" + "="*80)
print("2. TESTING AUTHENTICATION")
print("="*80)

def test_login_page():
    """Test login page"""
    try:
        response = client.get('/accounts/login/')
        if response.status_code == 200:
            results.add_pass("GET /accounts/login/")
        else:
            results.add_fail("GET /accounts/login/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /accounts/login/", str(e))

def test_register_page():
    """Test register page"""
    try:
        response = client.get('/accounts/register/')
        if response.status_code == 200:
            results.add_pass("GET /accounts/register/")
        else:
            results.add_fail("GET /accounts/register/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /accounts/register/", str(e))

def test_local_login_page():
    """Test local login page"""
    try:
        response = client.get('/accounts/login/local/')
        if response.status_code == 200:
            results.add_pass("GET /accounts/login/local/")
        else:
            results.add_fail("GET /accounts/login/local/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /accounts/login/local/", str(e))

test_login_page()
test_register_page()
test_local_login_page()

# ============================================================================
# 3. API ENDPOINTS TESTS
# ============================================================================
print("\n\n" + "="*80)
print("3. TESTING API ENDPOINTS")
print("="*80)

def test_blog_posts_api():
    """Test blog posts API"""
    try:
        response = client.get('/posts/api/posts/')
        if response.status_code == 200:
            results.add_pass("GET /posts/api/posts/")
        else:
            results.add_fail("GET /posts/api/posts/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /posts/api/posts/", str(e))

def test_search_api():
    """Test search API"""
    try:
        response = client.get('/search/api/?q=test')
        if response.status_code == 200:
            results.add_pass("GET /search/api/")
        else:
            results.add_fail("GET /search/api/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /search/api/", str(e))

def test_search_suggestions():
    """Test search suggestions API"""
    try:
        response = client.get('/dashboard/search-suggestions/?q=test')
        if response.status_code == 200:
            results.add_pass("GET /dashboard/search-suggestions/")
        else:
            results.add_fail("GET /dashboard/search-suggestions/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /dashboard/search-suggestions/", str(e))

def test_community_posts_api():
    """Test community posts API"""
    try:
        response = client.get('/dashboard/community-posts-api/')
        if response.status_code in [200, 302]:  # May require auth
            results.add_pass("GET /dashboard/community-posts-api/")
        else:
            results.add_fail("GET /dashboard/community-posts-api/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /dashboard/community-posts-api/", str(e))

def test_tag_options():
    """Test tag options API"""
    try:
        response = client.get('/recommend/tag-options/')
        if response.status_code == 200:
            results.add_pass("GET /recommend/tag-options/")
        else:
            results.add_fail("GET /recommend/tag-options/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /recommend/tag-options/", str(e))

test_blog_posts_api()
test_search_api()
test_search_suggestions()
test_community_posts_api()
test_tag_options()

# ============================================================================
# 4. CHATBOT TESTS
# ============================================================================
print("\n\n" + "="*80)
print("4. TESTING CHATBOT")
print("="*80)

def test_chatbot_page():
    """Test chatbot page"""
    try:
        response = client.get('/chatbot/')
        if response.status_code == 200:
            results.add_pass("GET /chatbot/")
        else:
            results.add_fail("GET /chatbot/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /chatbot/", str(e))

def test_chatbot_api():
    """Test chatbot API endpoint"""
    try:
        response = client.get('/chatbot/api/chat/')
        # GET without message is expected to fail or return empty
        if response.status_code in [200, 400, 405]:
            results.add_pass("GET /chatbot/api/chat/ (endpoint exists)")
        else:
            results.add_fail("GET /chatbot/api/chat/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /chatbot/api/chat/", str(e))

def test_chatbot_history():
    """Test chatbot history API"""
    try:
        response = client.get('/chatbot/api/history/')
        if response.status_code in [200, 302]:  # May require auth
            results.add_pass("GET /chatbot/api/history/")
        else:
            results.add_fail("GET /chatbot/api/history/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /chatbot/api/history/", str(e))

test_chatbot_page()
test_chatbot_api()
test_chatbot_history()

# ============================================================================
# 5. RECOMMENDATION SYSTEM TESTS
# ============================================================================
print("\n\n" + "="*80)
print("5. TESTING RECOMMENDATION SYSTEM")
print("="*80)

def test_recommendations():
    """Test recommendation endpoints"""
    try:
        response = client.get('/recommend/for-you/')
        if response.status_code in [200, 302]:  # May require auth
            results.add_pass("GET /recommend/for-you/")
        else:
            results.add_fail("GET /recommend/for-you/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /recommend/for-you/", str(e))

def test_user_interests():
    """Test user interests endpoint"""
    try:
        response = client.get('/recommend/interests/')
        if response.status_code in [200, 302]:  # May require auth
            results.add_pass("GET /recommend/interests/")
        else:
            results.add_fail("GET /recommend/interests/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /recommend/interests/", str(e))

def test_blog_recommendations():
    """Test blog recommendations"""
    try:
        response = client.get('/recommend/blog-recommendations/')
        if response.status_code in [200, 302]:
            results.add_pass("GET /recommend/blog-recommendations/")
        else:
            results.add_fail("GET /recommend/blog-recommendations/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /recommend/blog-recommendations/", str(e))

test_recommendations()
test_user_interests()
test_blog_recommendations()

# ============================================================================
# 6. ADMIN PANEL TESTS
# ============================================================================
print("\n\n" + "="*80)
print("6. TESTING ADMIN PANEL")
print("="*80)

def test_admin_panel():
    """Test admin panel access"""
    try:
        response = client.get('/admin/')
        if response.status_code in [200, 302]:  # 302 if not logged in
            results.add_pass("GET /admin/")
        else:
            results.add_fail("GET /admin/", f"Status: {response.status_code}")
    except Exception as e:
        results.add_error("GET /admin/", str(e))

test_admin_panel()

# ============================================================================
# 7. DATABASE AND MODELS TESTS
# ============================================================================
print("\n\n" + "="*80)
print("7. TESTING DATABASE & MODELS")
print("="*80)

def test_models_exist():
    """Test that all models are properly created"""
    try:
        # Test User model
        user_count = User.objects.count()
        results.add_pass(f"User model exists ({user_count} users)")
        
        # Test Profile model
        profile_count = Profile.objects.count()
        results.add_pass(f"Profile model exists ({profile_count} profiles)")
        
        # Test Post model
        post_count = Post.objects.count()
        results.add_pass(f"Post model exists ({post_count} posts)")
        
        # Test Community model
        community_count = Community.objects.count()
        results.add_pass(f"Community model exists ({community_count} communities)")
        
        # Test CommunityPost model
        community_post_count = CommunityPost.objects.count()
        results.add_pass(f"CommunityPost model exists ({community_post_count} posts)")
        
    except Exception as e:
        results.add_error("Models check", str(e))

test_models_exist()

# ============================================================================
# PRINT RESULTS
# ============================================================================
results.summary()

# Exit with appropriate code
exit_code = 0 if not results.failed and not results.errors else 1
sys.exit(exit_code)
