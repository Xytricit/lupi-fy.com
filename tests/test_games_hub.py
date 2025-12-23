from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from games.models import Game

User = get_user_model()


class GamesHubViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="games_user",
            email="games@example.com",
            password="gamespass123",
        )
        self.games = [
            Game.objects.create(
                title="Lupi Runner",
                slug="lupi-runner",
                owner=self.user,
                status="approved",
                visibility="public",
            ),
            Game.objects.create(
                title="Astro Builder",
                slug="astro-builder",
                owner=self.user,
                status="approved",
                visibility="public",
            ),
        ]

    def test_games_hub_provides_default_continue_playing(self):
        self.client.login(username="games_user", password="gamespass123")
        response = self.client.get(reverse("games_hub"))
        self.assertEqual(response.status_code, 200)
        context = response.context
        fallback = context.get("default_continue_playing")
        self.assertTrue(fallback)
        self.assertEqual(context.get("continue_playing"), fallback)
        self.assertEqual(len(fallback), len(self.games))
