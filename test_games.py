#!/usr/bin/env python
"""
Quick test script to verify games functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import LetterSetGame, GameLobbyChallenge, WordListGame

User = get_user_model()

# Create test user
username = 'testplayer'
user, created = User.objects.get_or_create(
    username=username,
    defaults={'email': 'test@example.com', 'is_email_verified': True}
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f"✓ Created test user: {username}")
else:
    print(f"✓ Test user exists: {username}")

# Test Letter Set Game creation
game, created = LetterSetGame.objects.get_or_create(user=user)
print(f"✓ Letter Set Game: {game.id} (letters: {game.letters}, score: {game.score})")

# Test Game Lobby Challenge creation
from accounts.views import generate_random_letter_list
challenge, created = GameLobbyChallenge.objects.get_or_create(
    user=user,
    defaults={
        'letters': generate_random_letter_list(12),
        'used_letters': [],
        'completed': False
    }
)
print(f"✓ Game Lobby Challenge: {challenge.id} (letters: {challenge.letters})")

# Test Word List Game
wgame, created = WordListGame.objects.get_or_create(user=user)
print(f"✓ Word List Game: {wgame.id} (score: {wgame.score})")

print("\n✅ All game models working!")
print(f"\nLogin with:\n  Username: {username}\n  Password: testpass123")
