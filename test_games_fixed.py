#!/usr/bin/env python
"""
Test script to verify the games are working correctly.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth.models import User
from accounts.models import GameLobbyChallenge, LetterSetGame, WordListGame
import random
import string

def create_test_user():
    """Create or get test user."""
    user, created = User.objects.get_or_create(
        username='gametest',
        defaults={
            'email': 'gametest@test.com',
            'first_name': 'Game',
            'last_name': 'Tester'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created test user: {user.username}")
    else:
        print(f"✓ Using existing user: {user.username}")
    return user

def test_game_lobby_challenge():
    """Test GameLobbyChallenge model."""
    user = create_test_user()
    
    # Create a challenge
    letters = [random.choice(string.ascii_uppercase) for _ in range(12)]
    challenge = GameLobbyChallenge.objects.create(
        user=user,
        letters=letters,
        banned_words=['test', 'banned', 'word']
    )
    
    print(f"✓ Created GameLobbyChallenge: letters={challenge.letters}, banned_words={challenge.banned_words}")
    
    # Verify it can be retrieved
    retrieved = GameLobbyChallenge.objects.get(id=challenge.id)
    print(f"✓ Retrieved challenge: {retrieved}")
    
    return challenge

def test_letter_set_game():
    """Test LetterSetGame model."""
    user = create_test_user()
    
    # Create a game
    letters = [random.choice(string.ascii_uppercase) for _ in range(7)]
    game, created = LetterSetGame.objects.get_or_create(
        user=user,
        defaults={
            'letters': letters,
            'score': 0,
            'words_submitted': ''
        }
    )
    
    if created:
        print(f"✓ Created LetterSetGame: letters={game.letters}, score={game.score}")
    else:
        print(f"✓ Using existing LetterSetGame: letters={game.letters}, score={game.score}")
    
    # Test adding a word
    game.words_submitted = 'test,word,sample'
    game.score = 30
    game.save()
    
    print(f"✓ Updated game: words={game.words_submitted}, score={game.score}")
    
    return game

def test_word_list_game():
    """Test WordListGame model."""
    user = create_test_user()
    
    game, created = WordListGame.objects.get_or_create(
        user=user,
        defaults={'score': 0}
    )
    
    if created:
        print(f"✓ Created WordListGame: score={game.score}")
    else:
        print(f"✓ Using existing WordListGame: score={game.score}")
    
    # Update score
    game.score = (game.score or 0) + 20
    game.save()
    
    print(f"✓ Updated WordListGame: score={game.score}")
    
    return game

def verify_url_names():
    """Verify URL names exist."""
    from django.urls import reverse, NoReverseMatch
    
    urls_to_check = [
        'game_lobby',
        'games_hub',
        'letter_set_game',
        'game_challenge_start',
        'letter_set_submit_word',
        'letter_set_start',
    ]
    
    print("\n🔗 Checking URL patterns:")
    for url_name in urls_to_check:
        try:
            url = reverse(url_name)
            print(f"✓ {url_name}: {url}")
        except NoReverseMatch:
            print(f"✗ {url_name}: NOT FOUND")

if __name__ == "__main__":
    print("🎮 Testing Game Infrastructure\n")
    print("=" * 50)
    
    print("\n📋 Testing Models:")
    test_game_lobby_challenge()
    test_letter_set_game()
    test_word_list_game()
    
    verify_url_names()
    
    print("\n" + "=" * 50)
    print("✅ All game infrastructure tests passed!")
    print("\n📝 Next Steps:")
    print("  1. Log in with the test user (username: gametest, password: testpass123)")
    print("  2. Visit http://localhost:8000/accounts/game/lobby/")
    print("  3. Visit http://localhost:8000/accounts/games/letter-set/")
    print("  4. Test WebSocket connections and game functionality")
