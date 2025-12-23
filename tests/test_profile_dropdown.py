
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileDropdownTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.client.login(username='testuser', password='password123')

    def test_profile_dropdown_content(self):
        """Test that the profile dropdown contains the expected user info and links."""
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check for user info in dropdown
        self.assertIn('testuser', content)
        self.assertIn('test@example.com', content)

        # Check for links
        self.assertIn(reverse('profile'), content)
        self.assertIn(reverse('chat_page'), content)
        self.assertIn(reverse('appearance'), content)
        self.assertIn(reverse('logout'), content)

        # Check for the new radix-powered dropdown structure
        self.assertIn('aria-controls="userMenuDropdown"', content)
        self.assertIn('data-radix-menu-content', content)
        self.assertIn('data-state="closed"', content)
        self.assertIn('data-side="bottom"', content)
        self.assertIn('data-align="end"', content)
        self.assertIn('radix-dropdown-content', content)
        self.assertIn('radix-dropdown-header', content)
        self.assertIn('radix-dropdown-item', content)

        # Check for icons (SVG parts)
        self.assertIn('lucide-user', content)
        self.assertIn('lucide-message-square', content)
        self.assertIn('lucide-settings', content)
        self.assertIn('lucide-log-out', content)
