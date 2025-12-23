from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from communities.models import Community, CommunityPost

User = get_user_model()

class CommunitiesUIUpdateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        
        # Create some dummy data
        self.community = Community.objects.create(
            name='Test Community',
            category='gaming',
            description='A test community',
            creator=self.user,
            banner_image='test_banner.jpg',
            community_image='test_logo.jpg',
            rules='Respect the community code.'
        )
        self.community.members.add(self.user)

    def test_communities_list_ui_classes(self):
        """Test that the communities list page uses the updated UI classes."""
        url = reverse('communities')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for new classes
        self.assertContains(response, 'class="filter-wrapper"', html=False)
        self.assertContains(response, 'class="filter-chip', html=False)
        self.assertContains(response, 'class="section-header"', html=False)
        
        # Check for absence of old classes
        self.assertNotContains(response, 'class="category-filters"')
        self.assertNotContains(response, 'class="category-filter-btn"')
        self.assertNotContains(response, 'class="communities-header"')
        
        # Check for absence of redundant theme script
        # The script contained "const serverTheme ="
        self.assertNotContains(response, 'const serverTheme =')

    def test_communities_list_content(self):
        """Test that the content is still rendered correctly."""
        url = reverse('communities')
        response = self.client.get(url)
        
        self.assertContains(response, 'Test Community')
        self.assertContains(response, 'Gaming')

    def test_community_detail_renders_hero_posts_sidebar(self):
        post = CommunityPost.objects.create(
            community=self.community,
            author=self.user,
            title='Sample Update',
            content='Sharing news about the community.'
        )
        url = reverse('community_detail', args=[self.community.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.community.name)
        self.assertContains(response, 'Latest posts')
        self.assertContains(response, post.title)
        self.assertContains(response, 'Leave Community')
        create_post_url = reverse('create_community_post', args=[self.community.id])
        self.assertContains(response, f'href="{create_post_url}"')
        self.assertContains(response, 'Members (1)')
        self.assertContains(response, 'Respect the community code.')
