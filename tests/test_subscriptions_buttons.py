"""
Unit tests for Subscriptions page Like/Dislike button functionality
Tests cover: button state persistence, count updates, mutual exclusivity
"""

import os
import django
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from blog.models import Post
from communities.models import Community, CommunityPost


class SubscriptionsLikeDislikeButtonTests(TestCase):
    """Test Like and Dislike button functionality on subscriptions page"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.User = get_user_model()
        
        # Create test users
        self.user1 = self.User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = self.User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create a test blog post
        self.blog_post = Post.objects.create(
            title='Test Blog Post',
            content='Test blog content',
            author=self.user2
        )
        
        # Create a test community and post
        self.community = Community.objects.create(
            name='Test Community',
            description='Test community description',
            creator=self.user2
        )
        self.community_post = CommunityPost.objects.create(
            title='Test Community Post',
            content='Test community content',
            community=self.community,
            author=self.user2
        )
        
        # Login as user1
        self.client.login(username='user1', password='testpass123')

    def test_like_button_increments_count(self):
        """Test that liking a blog post increments the like count"""
        # Initial like count should be 0
        initial_count = self.blog_post.likes.count()
        self.assertEqual(initial_count, 0)
        
        # Like the post via API
        response = self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('liked'))
        self.assertEqual(data.get('likes_count'), 1)
        
        # Verify count in database
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 1)
        self.assertIn(self.user1, self.blog_post.likes.all())

    def test_like_button_toggles_state(self):
        """Test that liking again removes the like"""
        # Like the post
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        
        # Verify liked
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 1)
        
        # Like again (should unlike)
        response = self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        data = json.loads(response.content)
        
        # Verify unliked
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 0)
        self.assertFalse(data.get('liked'))

    def test_dislike_button_toggles_state(self):
        """Test that disliking a post toggles correctly"""
        # Dislike the post
        response = self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('disliked'))
        self.assertEqual(data.get('dislikes_count'), 1)
        
        # Verify count in database
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.dislikes.count(), 1)
        self.assertIn(self.user1, self.blog_post.dislikes.all())

    def test_like_clears_dislike(self):
        """Test that liking clears dislike state"""
        # Dislike the post
        self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.dislikes.count(), 1)
        
        # Like the post (should clear dislike)
        response = self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        data = json.loads(response.content)
        
        # Verify like is set and dislike is cleared
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 1)
        self.assertEqual(self.blog_post.dislikes.count(), 0)
        self.assertIn(self.user1, self.blog_post.likes.all())

    def test_dislike_clears_like(self):
        """Test that disliking clears like state"""
        # Like the post
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 1)
        
        # Dislike the post (should clear like)
        response = self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        data = json.loads(response.content)
        
        # Verify dislike is set and like is cleared
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.dislikes.count(), 1)
        self.assertEqual(self.blog_post.likes.count(), 0)
        self.assertIn(self.user1, self.blog_post.dislikes.all())

    def test_community_post_like_button(self):
        """Test that liking a community post works"""
        # Like the community post
        response = self.client.post(f'/communities/api/post/{self.community_post.id}/like/')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('liked'))
        
        # Verify count in database
        self.community_post.refresh_from_db()
        self.assertEqual(self.community_post.likes.count(), 1)

    def test_like_button_persists_after_refresh(self):
        """Test that like state persists after page reload"""
        # Like the post
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        
        # Check persisted state
        response = self.client.get(reverse('post_detail', args=[self.blog_post.id]))
        self.assertEqual(response.status_code, 200)
        
        # Verify user is still in likes
        self.blog_post.refresh_from_db()
        self.assertIn(self.user1, self.blog_post.likes.all())

    def test_like_button_response_format(self):
        """Test that like button API returns correct response format"""
        response = self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Check required fields
        self.assertIn('liked', data)
        self.assertIn('likes_count', data)
        self.assertIn('dislikes_count', data)
        
        # Check types
        self.assertIsInstance(data['liked'], bool)
        self.assertIsInstance(data['likes_count'], int)
        self.assertIsInstance(data['dislikes_count'], int)

    def test_dislike_button_response_format(self):
        """Test that dislike button API returns correct response format"""
        response = self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Check required fields
        self.assertIn('disliked', data)
        self.assertIn('dislikes_count', data)
        self.assertIn('likes_count', data)
        
        # Check types
        self.assertIsInstance(data['disliked'], bool)
        self.assertIsInstance(data['dislikes_count'], int)
        self.assertIsInstance(data['likes_count'], int)

    def test_multiple_users_can_like_same_post(self):
        """Test that multiple users can like the same post"""
        # User 1 likes
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        
        # User 2 likes
        self.client.logout()
        self.client.login(username='user2', password='testpass123')
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        
        # Verify both users are in likes
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 2)
        self.assertIn(self.user1, self.blog_post.likes.all())
        self.assertIn(self.user2, self.blog_post.likes.all())


if __name__ == '__main__':
    import unittest
    unittest.main()
