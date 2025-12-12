"""Tests for recommendation system and interests onboarding."""

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from accounts.models import LetterSetGame, WordListGame
from recommend.models import UserInterests
from recommend.utils import categorize_game, record_game_play

User = get_user_model()


class InterestsOnboardingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_get_user_interests(self):
        """Test fetching user interests."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/recommend/interests/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("categories", data)
        self.assertIn("completed_onboarding", data)

    def test_save_user_interests(self):
        """Test saving user interests."""
        self.client.login(username="testuser", password="testpass123")
        payload = {"categories": ["word", "puzzle"]}
        response = self.client.post(
            "/recommend/interests/save/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])

        # Verify it was saved
        interests = UserInterests.objects.get(user=self.user)
        self.assertEqual(interests.categories, ["word", "puzzle"])
        self.assertTrue(interests.completed_onboarding)

    def test_for_you_api(self):
        """Test For You recommendations API."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/recommend/for-you/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("results", data)


class InteractionRecordingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_record_game_play(self):
        """Test recording game plays as interactions."""
        game = WordListGame.objects.create(
            user=self.user, words=["hello", "world"], score=100
        )
        interaction = record_game_play(self.user, game, "play", 1.0)
        self.assertIsNotNone(interaction)
        self.assertEqual(interaction.user, self.user)
        self.assertEqual(interaction.object_id, game.id)
        self.assertEqual(interaction.action, "play")

    def test_categorize_game(self):
        """Test game categorization."""
        game = WordListGame.objects.create(user=self.user, words=["hello", "world"])
        category = categorize_game(game)
        self.assertEqual(category, "word")

        game2 = LetterSetGame.objects.create(user=self.user, letters="abcdefgh")
        category2 = categorize_game(game2)
        self.assertEqual(category2, "word")
