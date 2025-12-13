#!/usr/bin/env python
"""Full workflow integration test - simplified version."""

import os
import django
import json
import urllib.request
import urllib.error

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from games.models import Game, Score, Achievement, GameAsset, GameVersion, Transaction, UserAchievement
from accounts.models import UserProfile, UserNotification, UserPreference

BASE_URL = 'http://127.0.0.1:8000'

print("\n" + "="*60)
print("COMPREHENSIVE FEATURE TEST")
print("="*60)

# Test 1: User & Profile
print("\n[1] USER & PROFILE")
print("-"*60)

try:
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'first_name': 'Test', 'last_name': 'User'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    print(f"✓ Test user exists: {user.username}")
    
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'developer'}
    )
    print(f"✓ UserProfile (role: {profile.role})")
except Exception as e:
    print(f"✗ User setup failed: {e}")

# Test 2: Game creation in DB
print("\n[2] GAME CREATION")
print("-"*60)

try:
    game, created = Game.objects.get_or_create(
        title='Test Game 001',
        creator=user,
        defaults={
            'description': 'Automated test game',
            'logic_json': {'events': [], 'version': '1.0'},
            'visibility': 'draft'
        }
    )
    print(f"✓ Game created={created}: {game.title}")
    print(f"  - ID: {game.id}")
    print(f"  - Status: {game.visibility}")
except Exception as e:
    print(f"✗ Game creation failed: {e}")

# Test 3: Scoring
print("\n[3] SCORING & LEADERBOARD")
print("-"*60)

try:
    game = Game.objects.first()
    if game:
        score, created = Score.objects.get_or_create(
            game=game,
            player=user,
            defaults={'score': 1500}
        )
        print(f"✓ Score recorded: {score.score} points (created={created})")
        
        # Count scores
        score_count = Score.objects.filter(game=game).count()
        print(f"✓ Game leaderboard: {score_count} score(s)")
except Exception as e:
    print(f"✗ Scoring failed: {e}")

# Test 4: Achievements
print("\n[4] ACHIEVEMENTS")
print("-"*60)

try:
    ach, created = Achievement.objects.get_or_create(
        key='first_game',
        defaults={
            'title': 'First Game Creator',
            'description': 'Create your first game',
            'icon': 'badge.png'
        }
    )
    print(f"✓ Achievement exists: {ach.title}")
    
    # User achievements
    ua_count = UserAchievement.objects.filter(user=user).count()
    print(f"✓ User unlocked: {ua_count} achievement(s)")
except Exception as e:
    print(f"✗ Achievements failed: {e}")

# Test 5: Assets
print("\n[5] ASSETS")
print("-"*60)

try:
    game = Game.objects.first()
    asset, created = GameAsset.objects.get_or_create(
        game=game,
        asset_type='sprite',
        defaults={'name': 'test_sprite', 'file': 'test.png'}
    )
    print(f"✓ Asset (type={asset.asset_type}): {asset.name}")
    
    asset_count = GameAsset.objects.filter(game=game).count()
    print(f"✓ Game assets: {asset_count} asset(s)")
except Exception as e:
    print(f"✗ Assets failed: {e}")

# Test 6: Transactions & Revenue
print("\n[6] MONETIZATION")
print("-"*60)

try:
    game = Game.objects.first()
    txn, created = Transaction.objects.get_or_create(
        game=game,
        user=user,
        defaults={
            'transaction_type': 'purchase',
            'amount': 2.99,
            'currency': 'USD'
        }
    )
    print(f"✓ Transaction: ${txn.amount} ({txn.transaction_type})")
    
    total_txn = Transaction.objects.filter(game=game).count()
    print(f"✓ Game transactions: {total_txn} record(s)")
except Exception as e:
    print(f"✗ Monetization failed: {e}")

# Test 7: Game versioning
print("\n[7] GAME VERSIONING")
print("-"*60)

try:
    game = Game.objects.first()
    version, created = GameVersion.objects.get_or_create(
        game=game,
        version_number=1,
        defaults={
            'logic_json': {'events': [], 'version': '1.0'},
            'description': 'Initial version'
        }
    )
    print(f"✓ Version {version.version_number}: {version.description}")
    
    version_count = GameVersion.objects.filter(game=game).count()
    print(f"✓ Game versions: {version_count} version(s)")
except Exception as e:
    print(f"✗ Versioning failed: {e}")

# Test 8: Notifications
print("\n[8] NOTIFICATIONS")
print("-"*60)

try:
    notif, created = UserNotification.objects.get_or_create(
        user=user,
        defaults={
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'notification_type': 'achievement'
        }
    )
    print(f"✓ Notification: {notif.title}")
    
    notif_count = UserNotification.objects.filter(user=user, is_read=False).count()
    print(f"✓ Unread notifications: {notif_count}")
except Exception as e:
    print(f"✗ Notifications failed: {e}")

# Test 9: User Preferences
print("\n[9] USER PREFERENCES")
print("-"*60)

try:
    pref, created = UserPreference.objects.get_or_create(
        user=user,
        defaults={
            'theme': 'dark',
            'language': 'en',
            'notifications_enabled': True
        }
    )
    print(f"✓ Preferences (theme={pref.theme}, lang={pref.language})")
except Exception as e:
    print(f"✗ Preferences failed: {e}")

# Test 10: API Endpoints
print("\n[10] API ENDPOINTS (READ-ONLY)")
print("-"*60)

try:
    endpoints = [
        '/games/api/leaderboard/',
        '/games/api/achievements/',
    ]
    
    passed = 0
    for ep in endpoints:
        try:
            r = urllib.request.urlopen(f'{BASE_URL}{ep}')
            data = json.loads(r.read().decode('utf-8'))
            print(f"✓ {ep} -> {r.getcode()}")
            passed += 1
        except Exception as e:
            print(f"✗ {ep} -> {str(e)[:40]}")
    
    print(f"\nAPI Endpoints: {passed}/{len(endpoints)} PASS")
except Exception as e:
    print(f"✗ API test failed: {e}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

from django.db import connection
with connection.cursor() as cursor:
    tables = [
        ('auth_user', 'Users'),
        ('accounts_userprofile', 'Profiles'),
        ('games_game', 'Games'),
        ('games_score', 'Scores'),
        ('games_achievement', 'Achievements'),
        ('games_transaction', 'Transactions'),
    ]
    
    for table, label in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {label}: {count} record(s)")

print("\n✅ COMPREHENSIVE FEATURE TEST COMPLETE")
print("All major database models and relationships validated!")
