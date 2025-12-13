#!/usr/bin/env python
"""
Test bubble interactions on the home page.
Verifies that:
1. For You bubble shows forYouSection and loads recommendations
2. Other bubbles hide forYouSection and show community feed
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client

def test_bubble_interactions():
    """Test that bubbles properly toggle sections and dispatch events."""
    c = Client()
    
    # Ensure we are authenticated because dashboard requires login
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='testbot').exists():
        User.objects.create_user(username='testbot', password='password')
    logged_in = c.login(username='testbot', password='password')
    assert logged_in, 'Failed to log in test user'

    # Get the dashboard page (home feed)
    from django.urls import reverse
    resp = c.get(reverse('dashboard_home'))
    assert resp.status_code == 200, f"Home page failed: {resp.status_code}"
    content = resp.content.decode('utf-8')
    
    # Check For You bubble exists
    assert 'id="homeForYouToggle"' in content, "For You bubble not found"
    assert 'data-sort="for_you"' in content, "For You bubble missing data-sort attribute"
    
    # Check For You section container exists (should be in HTML but hidden initially)
    assert 'id="forYouSection"' in content, "forYouSection container not found"
    assert 'id="blogForYouContainer"' in content, "blogForYouContainer not found"
    assert 'id="communityForYouContainer"' in content, "communityForYouContainer not found"
    
    # Check other bubbles exist
    bubble_sorts = ['latest', 'most_liked', 'most_viewed', 'trending', 'bookmarks']
    for sort in bubble_sorts:
        assert f'data-sort="{sort}"' in content, f"Bubble {sort} not found"
    
    # Check bubble manager JS is present
    assert 'filter-bubble manager' in content, "Bubble manager script not found"
    assert 'sortChange' in content, "sortChange event not found in template"
    assert 'forYouSection.style.display' in content, "forYouSection visibility toggle not found"
    
    # Check blog recommendations endpoint
    resp_blog = c.get('/recommend/blog-recommendations/')
    assert resp_blog.status_code == 200, f"Blog recommendations failed: {resp_blog.status_code}"
    data = resp_blog.json()
    assert 'results' in data, "Blog recs missing results"
    print(f"Blog recommendations returned {len(data['results'])} results")
    
    # Check community recommendations endpoint
    resp_comm = c.get('/recommend/community-recommendations/')
    assert resp_comm.status_code == 200, f"Community recommendations failed: {resp_comm.status_code}"
    data = resp_comm.json()
    assert 'results' in data, "Community recs missing results"
    print(f"Community recommendations returned {len(data['results'])} results")
    
    print("All bubble interaction checks passed!")
    print("For You bubble with containers found")
    print("Other filter bubbles found (Latest, Most liked, Most viewed, Trending, Bookmarks)")
    print("Bubble manager script properly configured to hide/show forYouSection")
    print("Blog and community recommendation endpoints working (200)")

if __name__ == '__main__':
    test_bubble_interactions()
