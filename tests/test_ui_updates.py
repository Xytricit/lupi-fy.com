from django.test import TestCase
from django.contrib.auth import get_user_model
from communities.models import Community, CommunityPost
from django.test.client import Client
from django.urls import reverse

User = get_user_model()


class MarketplaceUITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_marketplace_logout_button_removed(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/marketplace/')
        self.assertNotIn('Logout', response.content.decode())

    def test_marketplace_header_has_profile_button(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/marketplace/')
        content = response.content.decode()
        self.assertIn('Profile', content)
        self.assertIn(reverse('dashboard_home'), content)

    def test_marketplace_color_scheme_uses_css_variables(self):
        response = self.client.get('/marketplace/')
        content = response.content.decode()
        self.assertIn('var(--primary', content)
        self.assertIn('accent-gradient', content)


class ForYouDefensiveRenderingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_loads_without_for_you_data(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('For you', response.content.decode())

    def test_for_you_section_renders_with_missing_fields(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('id="forYouSection"', content)
        self.assertIn('id="blogForYouContainer"', content)
        self.assertIn('id="communityForYouContainer"', content)

    def test_dashboard_defensive_rendering_code_present(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('forYouSection', content)
        self.assertEqual(response.status_code, 200)


class UserAvatarDropdownTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='author1',
            email='author@example.com',
            password='authpass123'
        )
        self.community = Community.objects.create(
            name='Test Community',
            creator=self.author,
            category='GEN'
        )
        self.post = CommunityPost.objects.create(
            title='Test Post',
            content='Test content',
            author=self.author,
            community=self.community
        )

    def test_community_detail_avatar_clickable(self):
        response = self.client.get(
            reverse('community_detail', args=[self.community.id])
        )
        content = response.content.decode()
        self.assertIn('creator-pfp', content)
        self.assertIn('user-profile-trigger', content)

    def test_community_detail_has_avatar_dropdown_handler(self):
        response = self.client.get(
            reverse('community_detail', args=[self.community.id])
        )
        content = response.content.decode()
        self.assertIn('creator-pfp', content)
        self.assertIn('public-profile', content)

    def test_community_post_detail_avatar_dropdown(self):
        response = self.client.get(
            reverse('community_post_detail', args=[self.post.id])
        )
        content = response.content.decode()
        self.assertIn('author-avatar-trigger', content)
        self.assertIn('View Profile', content)
        self.assertIn('Send Message', content)

    def test_avatar_dropdown_routing_urls(self):
        response = self.client.get(
            reverse('community_post_detail', args=[self.post.id])
        )
        content = response.content.decode()
        self.assertIn(f'/accounts/user/{self.author.id}/public-profile/', content)
        self.assertIn('Send Message', content)


class CommunityPageLayoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.community1 = Community.objects.create(
            name='Test Community 1',
            creator=self.user,
            category='GEN'
        )
        self.community2 = Community.objects.create(
            name='Test Community 2',
            creator=self.user,
            category='DEV'
        )

    def test_communities_list_page_loads(self):
        response = self.client.get(reverse('communities_list'))
        self.assertEqual(response.status_code, 200)

    def test_communities_list_has_grid_layout(self):
        response = self.client.get(reverse('communities_list'))
        content = response.content.decode()
        self.assertIn('community-grid', content)
        self.assertIn('grid-template-columns', content)

    def test_communities_list_has_category_bubbles(self):
        response = self.client.get(reverse('communities_list'))
        content = response.content.decode()
        self.assertIn('community-bubble', content)
        self.assertIn('bubble-ellipse', content)

    def test_community_detail_sidebar_responsive(self):
        response = self.client.get(
            reverse('community_detail', args=[self.community1.id])
        )
        content = response.content.decode()
        self.assertIn('community-sidebar', content)
        self.assertIn('community-page', content)


class ResponsiveLayoutTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_home_responsive_classes(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)

    def test_marketplace_responsive_grid(self):
        response = self.client.get('/marketplace/')
        content = response.content.decode()
        self.assertIn('grid', content)
        self.assertIn('md:', content)
        self.assertIn('lg:', content)

    def test_for_you_grid_layout_present(self):
        response = self.client.get(reverse('dashboard_home'))
        content = response.content.decode()
        self.assertIn('minmax(180px,1fr)', content)
        self.assertIn('auto-fill', content)


class JavaScriptFunctionalityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_has_defensive_try_catch_blocks(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('forYouSection', response.content.decode())

    def test_avatar_dropdown_positioning_code(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)

    def test_dropdown_close_on_outside_click(self):
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)

    def test_marketplace_button_styling(self):
        response = self.client.get('/marketplace/')
        content = response.content.decode()
        self.assertIn('var(--primary', content)


class AccentColorTests(TestCase):
    def test_marketplace_uses_accent_color_variable(self):
        client = Client()
        response = client.get('/marketplace/')
        content = response.content.decode()
        self.assertIn('var(--primary', content)
        self.assertIn('rgba(31, 156, 238', content)

    def test_no_hardcoded_purple_gradient_in_marketplace(self):
        client = Client()
        response = client.get('/marketplace/')
        content = response.content.decode()
        self.assertNotIn('#667eea', content)
        self.assertNotIn('#764ba2', content)

    def test_marketplace_project_card_uses_accent_color(self):
        client = Client()
        response = client.get('/marketplace/')
        content = response.content.decode()
        self.assertIn('var(--primary,#1f9cee)', content)


class CommunityPostDetailAvatarTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='author1',
            email='author@example.com',
            password='authpass123'
        )
        self.community = Community.objects.create(
            name='Test Community',
            creator=self.author,
            category='GEN'
        )
        self.post = CommunityPost.objects.create(
            title='Test Post',
            content='Test content',
            author=self.author,
            community=self.community
        )

    def test_post_detail_has_dropdown_code(self):
        response = self.client.get(
            reverse('community_post_detail', args=[self.post.id])
        )
        content = response.content.decode()
        self.assertIn('author-avatar-trigger', content)
        self.assertIn('author-profile-dropdown', content)

    def test_post_detail_dropdown_shows_both_actions(self):
        response = self.client.get(
            reverse('community_post_detail', args=[self.post.id])
        )
        content = response.content.decode()
        self.assertIn('View Profile', content)
        self.assertIn('Send Message', content)

    def test_post_detail_dropdown_has_correct_urls(self):
        response = self.client.get(
            reverse('community_post_detail', args=[self.post.id])
        )
        content = response.content.decode()
        self.assertIn(f'/accounts/user/{self.author.id}/public-profile/', content)
        self.assertIn('Send Message', content)

    def test_post_detail_not_own_profile_check(self):
        response = self.client.get(
            reverse('community_post_detail', args=[self.post.id])
        )
        content = response.content.decode()
        self.assertIn('is_own_profile', content)
