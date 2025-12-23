"""
Integration tests for subscription page functionality.
Tests Like, Dislike, Bookmark, Link navigation, and Report functionality.
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from blog.models import Post
from communities.models import Community, CommunityPost
from accounts.models import CustomUser, Subscription


class SubscriptionPageIntegrationTests(TestCase):
    """Integration tests for subscription page buttons and links"""
    
    def setUp(self):
        """Set up test users, posts, and subscriptions"""
        # Create test users
        self.user1 = CustomUser.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = CustomUser.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Create test blog post
        self.blog_post = Post.objects.create(
            title='Test Blog Post',
            content='Test blog content',
            author=self.user2
        )
        
        # Create test community and post
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
        
        # Subscribe user1 to community and author
        self.community.members.add(self.user1)
        Subscription.objects.create(user=self.user1, community=self.community)
        Subscription.objects.create(user=self.user1, author=self.user2)
        
        # Initialize test client
        self.client = Client()
        self.client.login(username='user1', password='testpass123')
    
    def test_subscriptions_page_loads(self):
        """Test that subscriptions page loads successfully"""
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Subscriptions')
    
    def test_like_button_increments_blog_post(self):
        """Test Like button increments blog post count on subscription page"""
        response = self.client.post(
            f'/posts/post/{self.blog_post.id}/like/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('liked'))
        self.assertEqual(data.get('likes_count'), 1)
    
    def test_dislike_button_increments_blog_post(self):
        """Test Dislike button increments blog post count"""
        response = self.client.post(
            f'/posts/post/{self.blog_post.id}/dislike/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('disliked'))
        self.assertEqual(data.get('dislikes_count'), 1)
    
    def test_like_dislike_mutual_exclusivity(self):
        """Test that liking clears dislike and vice versa"""
        # Dislike post
        self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.dislikes.count(), 1)
        
        # Like post (should clear dislike)
        response = self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        self.blog_post.refresh_from_db()
        
        self.assertEqual(self.blog_post.likes.count(), 1)
        self.assertEqual(self.blog_post.dislikes.count(), 0)
        
        # Dislike again (should clear like)
        response = self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        self.blog_post.refresh_from_db()
        
        self.assertEqual(self.blog_post.dislikes.count(), 1)
        self.assertEqual(self.blog_post.likes.count(), 0)
    
    def test_bookmark_button_blog_post(self):
        """Test bookmark button for blog post"""
        # Initially not bookmarked
        self.assertNotIn(self.blog_post, self.user1.bookmarked_posts.all())
        
        # Bookmark
        response = self.client.post(
            f'/posts/post/{self.blog_post.id}/bookmark/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify bookmarked
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertIn(self.blog_post, self.user1.bookmarked_posts.all())
    
    def test_bookmark_button_community_post(self):
        """Test bookmark button for community post"""
        # Initially not bookmarked
        self.assertNotIn(self.community_post, self.user1.bookmarked_community_posts.all())
        
        # Bookmark
        response = self.client.post(
            f'/communities/api/post/{self.community_post.id}/bookmark/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify bookmarked
        self.assertEqual(response.status_code, 200)
        self.user1.refresh_from_db()
        self.assertIn(self.community_post, self.user1.bookmarked_community_posts.all())
    
    def test_blog_post_link_navigation(self):
        """Test that blog post link navigates to correct detail page"""
        response = self.client.get(reverse('post_detail', args=[self.blog_post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.blog_post.title)
    
    def test_community_post_link_navigation(self):
        """Test that community post link navigates to correct detail page"""
        response = self.client.get(
            reverse('community_post_detail', args=[self.community_post.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.community_post.title)
    
    def test_report_blog_post(self):
        """Test report functionality for blog post"""
        response = self.client.post(
            f'/posts/post/{self.blog_post.id}/report/',
            data=json.dumps({'reason': 'Inappropriate content'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should be successful (or redirect to handle report)
        self.assertIn(response.status_code, [200, 201, 302])
    
    def test_report_community_post(self):
        """Test report functionality for community post"""
        response = self.client.post(
            f'/communities/api/post/{self.community_post.id}/report/',
            data=json.dumps({'reason': 'Inappropriate content'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should be successful (or redirect to handle report)
        self.assertIn(response.status_code, [200, 201, 302])
    
    def test_like_toggles_correctly(self):
        """Test that liking same post twice toggles like off"""
        # Like
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 1)
        
        # Like again (should unlike)
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 0)
    
    def test_dislike_toggles_correctly(self):
        """Test that disliking same post twice toggles dislike off"""
        # Dislike
        self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.dislikes.count(), 1)
        
        # Dislike again (should un-dislike)
        self.client.post(f'/posts/post/{self.blog_post.id}/dislike/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.dislikes.count(), 0)
    
    def test_community_like_button(self):
        """Test community post like button"""
        response = self.client.post(
            f'/communities/api/post/{self.community_post.id}/like/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('liked'))
        self.assertEqual(data.get('likes_count'), 1)
    
    def test_community_dislike_button(self):
        """Test community post dislike button"""
        response = self.client.post(
            f'/communities/api/post/{self.community_post.id}/dislike/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('disliked'))
        self.assertEqual(data.get('dislikes_count'), 1)
    
    def test_multiple_users_like_same_post(self):
        """Test that multiple users can like the same post"""
        # User1 likes
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        self.blog_post.refresh_from_db()
        self.assertEqual(self.blog_post.likes.count(), 1)
        
        # User2 likes
        self.client.logout()
        self.client.login(username='user2', password='testpass123')
        self.client.post(f'/posts/post/{self.blog_post.id}/like/')
        self.blog_post.refresh_from_db()
        
        # Both should be in likes
        self.assertEqual(self.blog_post.likes.count(), 2)
        self.assertIn(self.user1, self.blog_post.likes.all())
        self.assertIn(self.user2, self.blog_post.likes.all())
    
    def test_bookmarked_posts_api_returns_bookmark(self):
        """Test that bookmarked posts API returns bookmarked content"""
        self.client.post(
            f'/communities/api/post/{self.community_post.id}/bookmark/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        response = self.client.get(reverse('bookmarked_posts_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        titles = [item.get('title') for item in data.get('items', [])]
        self.assertIn(self.community_post.title, titles)
    
    def test_subscription_posts_api_returns_subscribed_posts(self):
        """Test that subscription posts API returns community posts"""
        response = self.client.get(reverse('subscription_posts_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        ids = [item.get('id') for item in data.get('items', [])]
        self.assertIn(self.community_post.id, ids)
    
    def test_subscription_blogs_api_returns_followed_blogs(self):
        """Test that subscription blogs API returns followed authors"""
        response = self.client.get(reverse('subscription_blogs_api'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        ids = [item.get('id') for item in data.get('items', [])]
        self.assertIn(self.blog_post.id, ids)


class SubscriptionPageAuthenticationTests(TestCase):
    """Test authentication and access control on subscription page"""
    
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.blog_post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
    
    def test_subscriptions_page_requires_login(self):
        """Test that subscriptions page requires login"""
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_like_button_requires_login(self):
        """Test that like button requires login"""
        response = self.client.post(
            f'/posts/post/{self.blog_post.id}/like/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertIn(response.status_code, [302, 401])  # Redirect or unauthorized


class SubscriptionPageErrorHandlingTests(TestCase):
    """Test error handling on subscription page"""
    
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_like_nonexistent_post(self):
        """Test liking a non-existent post returns 404"""
        response = self.client.post(
            '/posts/post/99999/like/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_dislike_nonexistent_post(self):
        """Test disliking a non-existent post returns 404"""
        response = self.client.post(
            '/posts/post/99999/dislike/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)
    
    def test_like_nonexistent_community_post(self):
        """Test liking a non-existent community post returns 404"""
        response = self.client.post(
            '/communities/api/post/99999/like/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 404)
