from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from accounts.models import Badge, BadgeRequirementType, UserBadge
from blog.models import Post


User = get_user_model()


class AccountDashboardPrivacyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="privacyuser",
            email="privacy@example.com",
            password="secret123",
        )
        self.client.login(username="privacyuser", password="secret123")

    def test_profile_section_hides_allow_dms_toggle(self):
        url = f"{reverse('account_dashboard')}?section=profile"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn('Allow people to send me direct messages', content)
        self.assertNotIn('name="allow_dms"', content)

    def test_social_section_retains_allow_dms_toggle(self):
        url = f"{reverse('account_dashboard')}?section=social"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Allow people to send me direct messages', content)
        self.assertIn('name="allow_dms"', content)


class AccountDashboardAchievementsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="badgeuser",
            email="badge@example.com",
            password="secret123",
        )
        self.client.login(username="badgeuser", password="secret123")
        Badge.objects.all().delete()
        UserBadge.objects.all().delete()

    def test_achievements_page_displays_locked_and_unlocked_badges(self):
        first_badge = Badge.objects.create(
            name="First Post",
            description="Write your first community post.",
            requirement_type=BadgeRequirementType.POSTS_CREATED,
            requirement_value=1,
            tier="Bronze",
        )
        Badge.objects.create(
            name="Community Storyteller",
            description="Publish five posts in total.",
            requirement_type=BadgeRequirementType.POSTS_CREATED,
            requirement_value=5,
            tier="Silver",
        )

        Post.objects.create(
            author=self.user,
            title="Hello World",
            content="This is my first post.",
            description="Intro post",
        )

        url = f"{reverse('account_dashboard')}?section=achievements"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode()
        self.assertIn('data-badge-unlocked="True"', content)
        self.assertIn('data-badge-unlocked="False"', content)
        self.assertIn("1 / 2 earned", content)
        self.assertEqual(content.count('Unlocked'), 1)
        self.assertEqual(content.count('Locked'), 1)
        self.assertIn(first_badge.name, content)
        self.assertIn("Community Storyteller", content)
