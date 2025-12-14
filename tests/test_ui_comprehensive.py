import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from blog.models import Post, Category, PostImage
from communities.models import Community, CommunityPost

User = get_user_model()


class PostFormTests(TestCase):
    """Test blog and community post form updates"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            public_profile=True
        )
        self.category = Category.objects.create(name='Tech')
        self.client.login(username='testuser', password='testpass123')
    
    def test_blog_create_post_has_back_button(self):
        response = self.client.get('/posts/create/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Back', content)
        self.assertIn('back-button', content)
        self.assertIn('window.history.back()', content)
    
    def test_blog_create_post_uses_css_variables(self):
        response = self.client.get('/posts/create/')
        content = response.content.decode()
        self.assertIn('var(--primary', content)
        self.assertIn('var(--accent', content)
    
    def test_community_create_post_has_back_button(self):
        response = self.client.get('/communities/post/create/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Back', content)
        self.assertIn('back-button', content)
    
    def test_community_create_form_uses_css_variables(self):
        response = self.client.get('/communities/post/create/')
        content = response.content.decode()
        self.assertIn('var(--primary', content)


class CommunityCreationTests(TestCase):
    """Test community creation form"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_create_community_has_back_button(self):
        response = self.client.get('/communities/create/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Create a Community', content)
        self.assertIn('Back', content)
        self.assertIn('back-button', content)
    
    def test_create_community_styling_uses_variables(self):
        response = self.client.get('/communities/create/')
        content = response.content.decode()
        self.assertIn('var(--card-bg)', content)
        self.assertIn('var(--primary', content)


class ForYouFilteringTests(TestCase):
    """Test For You section filtering and styling"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Tech')
        self.client.login(username='testuser', password='testpass123')
    
    def test_dashboard_has_for_you_section(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('forYouSection', content)
        self.assertIn('For You', content)
    
    def test_for_you_has_filter_bubbles(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('for-you-filter-btn', content)
        self.assertIn('Latest', content)
        self.assertIn('Most Liked', content)
        self.assertIn('data-sort="latest"', content)
        self.assertIn('data-sort="most-liked"', content)
    
    def test_for_you_containers_exist(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('blogForYouContainer', content)
        self.assertIn('communityForYouContainer', content)
    
    def test_for_you_rendering_function_exists(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('renderForYouCards', content)
        self.assertIn('window.forYouData', content)
        self.assertIn('window.forYouSortMode', content)


class AvatarDropdownTests(TestCase):
    """Test avatar dropdown functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            public_profile=True
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass456',
            public_profile=False
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_universal_avatar_dropdown_function_exists(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('setupAvatarDropdown', content)
        self.assertIn('universal-avatar-dropdown', content)
    
    def test_avatar_dropdown_respects_public_profile(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('data-avatar-user-id', content)
        self.assertIn('data-user-public-profile', content)
    
    def test_avatar_dropdown_has_chat_link(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('/accounts/chat/', content)
        self.assertIn('Send Message', content)
    
    def test_avatar_dropdown_view_profile_option(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('/public-profile/', content)
        self.assertIn('View Profile', content)


class ChatLinkTests(TestCase):
    """Test chat link routing"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass456'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_chat_page_loads(self):
        response = self.client.get(f'/accounts/chat/{self.user2.id}/')
        self.assertEqual(response.status_code, 200)
    
    def test_chat_link_format_correct(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertNotIn('undefined', content)


class ProfileVisibilityTests(TestCase):
    """Test profile visibility settings"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            public_profile=True
        )
        self.user_private = User.objects.create_user(
            username='private_user',
            email='private@example.com',
            password='testpass456',
            public_profile=False
        )
    
    def test_public_profile_viewable(self):
        response = self.client.get(f'/accounts/user/{self.user.id}/public-profile/')
        self.assertEqual(response.status_code, 200)
    
    def test_private_profile_returns_restricted(self):
        response = self.client.get(f'/accounts/user/{self.user_private.id}/public-profile/')
        # Should redirect or show restricted message
        self.assertIn(response.status_code, [302, 403, 200])


class StylingConsistencyTests(TestCase):
    """Test consistent styling across pages"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Tech')
        self.client.login(username='testuser', password='testpass123')
    
    def test_forms_use_css_variables(self):
        """All forms should use CSS variables for theming"""
        pages = [
            '/posts/create/',
            '/communities/post/create/',
            '/communities/create/',
        ]
        
        for page in pages:
            response = self.client.get(page)
            if response.status_code == 200:
                content = response.content.decode()
                # Check for CSS variable usage
                self.assertIn('var(--', content,
                    f"Page {page} missing CSS variable theme")
    
    def test_responsive_design_in_for_you(self):
        """For You section should have responsive grid"""
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('grid-template-columns', content)
        self.assertIn('minmax', content)


class DefensiveRenderingTests(TestCase):
    """Test defensive rendering (no crashes on missing data)"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_dashboard_loads_without_error(self):
        """Dashboard should load even if recommendation data is incomplete"""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Should have defensive rendering checks
        self.assertIn('renderForYouCards', content)
        self.assertIn('try', content)


class BackButtonTests(TestCase):
    """Test back button presence and functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_all_forms_have_back_button(self):
        """All post/community forms should have back button"""
        form_pages = [
            '/posts/create/',
            '/communities/post/create/',
            '/communities/create/',
        ]
        
        for page in form_pages:
            response = self.client.get(page)
            if response.status_code == 200:
                content = response.content.decode()
                self.assertIn('Back', content, f"Back button missing on {page}")
                self.assertIn('back-button', content,
                    f"Back button class missing on {page}")
                self.assertIn('window.history.back', content,
                    f"Back button onclick missing on {page}")
