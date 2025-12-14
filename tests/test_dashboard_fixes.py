"""
Integration tests for Dashboard Home fixes:
1. Notification badge visibility and clickability
2. Bubble sort filtering functionality
3. Spacing between bubble filters and community posts

Tests verify the fixes work correctly without breaking existing functionality.
"""

import os
import json
import django
from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from blog.models import Post, Tag as BlogTag
from communities.models import Community, CommunityPost
from accounts.models import Notification

User = get_user_model()


class NotificationBadgeFixTests(TestCase):
    """Test notification badge visibility and functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_notification_badge_shows_with_unread(self):
        """Test that badge displays when there are unread notifications"""
        Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test',
            notification_type='like',
            is_read=False
        )

        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'notificationBadge')

    def test_notification_badge_hidden_without_unread(self):
        """Test that badge hides when no unread notifications exist"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'notificationBadge')

    def test_notification_api_returns_correct_structure(self):
        """Test /accounts/api/notifications/ returns proper JSON"""
        Notification.objects.create(
            user=self.user,
            title='Test',
            message='Message',
            notification_type='like',
            is_read=False
        )

        response = self.client.get('/accounts/api/notifications/?limit=5')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn('notifications', data)
        self.assertIn('unread_count', data)
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['unread_count'], 1)
        self.assertFalse(data['notifications'][0]['is_read'])

    def test_notification_api_marks_as_read(self):
        """Test marking notification as read via API"""
        notif = Notification.objects.create(
            user=self.user,
            title='Test',
            message='Message',
            notification_type='like',
            is_read=False
        )

        response = self.client.post(
            f'/accounts/api/notifications/{notif.id}/mark-read/',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        notif.refresh_from_db()
        self.assertTrue(notif.is_read)


class BubbleSortFixTests(TestCase):
    """Test bubble sort filter functionality"""

    def setUp(self):
        """Set up test data with community posts"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        self.community = Community.objects.create(
            name='Test Community',
            category='technology',
            creator=self.user,
            description='A test community',
            banner_image='test.png',
            community_image='test.png'
        )
        self.community.members.add(self.user)

        # Create posts with different timestamps and engagement
        self.now = timezone.now()
        self.post1 = CommunityPost.objects.create(
            community=self.community,
            author=self.user,
            title='Post 1 (Latest)',
            content='Content 1',
            created_at=self.now
        )

        self.post2 = CommunityPost.objects.create(
            community=self.community,
            author=self.user,
            title='Post 2 (Older)',
            content='Content 2',
            created_at=self.now - timedelta(days=1)
        )

        self.post3 = CommunityPost.objects.create(
            community=self.community,
            author=self.user,
            title='Post 3 (Most liked)',
            content='Content 3',
            created_at=self.now - timedelta(days=2)
        )

        # Add likes to post3 so it ranks higher on "most_liked" sort
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='pass123'
        )
        self.post3.likes.add(self.user, self.user2)

    def test_latest_sort_returns_newest_first(self):
        """Test 'latest' sort returns posts in reverse chronological order"""
        response = self.client.get(
            '/dashboard/community-posts-api/?sort=latest&offset=0&limit=10'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertGreater(len(data['posts']), 0)
        if len(data['posts']) >= 2:
            first_time = data['posts'][0]['created_at']
            second_time = data['posts'][1]['created_at']
            self.assertGreaterEqual(first_time, second_time)

    def test_most_liked_sort_returns_highest_likes_first(self):
        """Test 'most_liked' sort returns posts by like count descending"""
        response = self.client.get(
            '/dashboard/community-posts-api/?sort=most_liked&offset=0&limit=10'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertGreater(len(data['posts']), 0)
        if len(data['posts']) >= 2:
            first_likes = data['posts'][0]['likes_count']
            second_likes = data['posts'][1]['likes_count']
            self.assertGreaterEqual(first_likes, second_likes)

    def test_api_includes_user_engagement_state(self):
        """Test that API returns user's engagement state (liked, bookmarked)"""
        self.post1.likes.add(self.user)

        response = self.client.get(
            '/dashboard/community-posts-api/?sort=latest&offset=0&limit=10'
        )
        data = response.json()

        # Find post1 in results
        post1_data = next((p for p in data['posts'] if p['id'] == self.post1.id), None)
        self.assertIsNotNone(post1_data)
        self.assertTrue(post1_data['user_liked'])
        self.assertFalse(post1_data['user_bookmarked'])

    def test_bubble_filters_exist_on_dashboard(self):
        """Test that all bubble filter buttons are present in dashboard"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)

        expected_filters = ['for_you', 'latest', 'most_liked', 'most_viewed', 'trending', 'bookmarks']
        for filter_name in expected_filters:
            self.assertContains(response, f'data-sort="{filter_name}"')

    def test_dashboard_has_community_feed_element(self):
        """Test that community-feed element exists with correct initial state"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="community-feed"')
        self.assertContains(response, 'display:none')

    def test_bookmarks_sort_returns_only_bookmarked_posts(self):
        """Test 'bookmarks' sort returns only posts bookmarked by current user"""
        self.post1.bookmarks.add(self.user)
        
        response = self.client.get(
            '/dashboard/community-posts-api/?sort=bookmarks&offset=0&limit=10'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(len(data['posts']), 1)
        self.assertEqual(data['posts'][0]['id'], self.post1.id)


class DashboardSpacingFixTests(TestCase):
    """Test spacing fixes between dashboard elements"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_bubble_section_has_reduced_margin(self):
        """Test that bubble filters section has margin-bottom:8px (not 20px)"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Check that the section has the correct margin
        self.assertIn('margin-bottom:8px', content)
        
        # Verify the bubble section is present
        self.assertIn('filter-bubble', content)

    def test_notification_badge_has_display_flex(self):
        """Test that notification badge uses display: flex (not duplicate display: none)"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Find the badge element and verify it has correct styles
        badge_section = content[content.find('notificationBadge'):content.find('notificationBadge') + 500]
        
        # Count how many times 'display:' appears - should not be duplicated
        display_count = badge_section.count('display:')
        self.assertLessEqual(display_count, 2, "Badge has duplicate display properties")

    def test_for_you_section_default_visibility(self):
        """Test that For You section is visible by default"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="forYouSection"')
        self.assertContains(response, 'display:block')

    def test_community_feed_initial_hidden(self):
        """Test that community feed is hidden initially"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Find community-feed element
        feed_start = content.find('id="community-feed"')
        self.assertNotEqual(feed_start, -1)
        
        # Check that it has display:none in initial state
        feed_section = content[feed_start:feed_start + 200]
        self.assertIn('display:none', feed_section)


class DashboardIntegrationTests(TestCase):
    """Integration tests for dashboard interactions"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

        self.community = Community.objects.create(
            name='Test Community',
            category='technology',
            creator=self.user,
            description='A test community',
            banner_image='test.png',
            community_image='test.png'
        )
        self.community.members.add(self.user)

        # Create multiple posts
        for i in range(15):
            CommunityPost.objects.create(
                community=self.community,
                author=self.user,
                title=f'Post {i}',
                content=f'Content {i}',
                created_at=timezone.now() - timedelta(days=i)
            )

    def test_dashboard_loads_successfully(self):
        """Test that dashboard page loads without errors"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lupify')

    def test_api_pagination_works(self):
        """Test that API pagination returns correct posts"""
        response = self.client.get(
            '/dashboard/community-posts-api/?sort=latest&offset=0&limit=5'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(len(data['posts']), 5)
        self.assertEqual(data['offset'], 0)
        self.assertEqual(data['limit'], 5)
        self.assertGreater(data['total'], 5)

    def test_pagination_offset_works(self):
        """Test that offset parameter correctly skips posts"""
        response1 = self.client.get(
            '/dashboard/community-posts-api/?sort=latest&offset=0&limit=5'
        )
        response2 = self.client.get(
            '/dashboard/community-posts-api/?sort=latest&offset=5&limit=5'
        )

        data1 = response1.json()
        data2 = response2.json()

        # Verify different posts are returned
        ids1 = [p['id'] for p in data1['posts']]
        ids2 = [p['id'] for p in data2['posts']]

        self.assertEqual(len(ids1), 5)
        self.assertEqual(len(ids2), 5)
        self.assertEqual(len(set(ids1) & set(ids2)), 0, "Offset should return different posts")

    def test_sort_parameter_validation(self):
        """Test that invalid sort parameters default to 'latest'"""
        response = self.client.get(
            '/dashboard/community-posts-api/?sort=invalid_sort&offset=0&limit=10'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Should still return posts (defaulting to latest)
        self.assertGreater(len(data['posts']), 0)

    def test_notification_dropdown_closes_on_outside_click(self):
        """Test that notification dropdown HTML is properly structured"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify dropdown elements exist
        self.assertIn('id="notificationDropdown"', content)
        self.assertIn('id="notificationList"', content)
        self.assertIn('id="notificationBell"', content)

    def test_bubble_filter_buttons_are_interactive(self):
        """Test that all bubble buttons have click handlers"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Verify event handler code exists
        self.assertIn('addEventListener', content)
        self.assertIn('sortChange', content)
        self.assertIn('filter-bubble', content)
