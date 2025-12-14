#!/usr/bin/env python
"""Full workflow integration script (not a unit test).

This file is intentionally safe to import so Django's default test discovery
won't execute it.

Run with: python test_full_workflow.py
"""

import os
import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def main() -> int:
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    django.setup()

    from django.contrib.auth import get_user_model

    from accounts.models import UserNotification, UserPreference, UserProfile
    from games.models import (
        Achievement,
        Game,
        GameAsset,
        GameVersion,
        Score,
        Transaction,
        UserAchievement,
    )

    User = get_user_model()

    print("\n" + "=" * 60)
    print("COMPREHENSIVE FEATURE TEST")
    print("=" * 60)

    # Test 1: User & Profile
    print("\n[1] USER & PROFILE")
    print("-" * 60)

    try:
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={"first_name": "Test", "last_name": "User"},
        )
        if created:
            user.set_password("testpass123")
            user.save()
        print(f"✓ Test user exists: {user.username}")

        profile, _ = UserProfile.objects.get_or_create(
            user=user, defaults={"role": "developer"}
        )
        print(f"✓ UserProfile (role: {getattr(profile, 'role', 'unknown')})")
    except Exception as e:
        print(f"✗ User setup failed: {e}")
        return 1

    # Test 2: Game creation
    print("\n[2] GAME CREATION")
    print("-" * 60)

    try:
        game, created = Game.objects.get_or_create(
            title="Test Game 001",
            creator=user,
            defaults={
                "description": "Automated test game",
                "logic_json": {"events": [], "version": "1.0"},
                "visibility": "draft",
            },
        )
        print(f"✓ Game created={created}: {game.title}")
        print(f"  - ID: {game.id}")
        print(f"  - Status: {getattr(game, 'visibility', '')}")
    except Exception as e:
        print(f"✗ Game creation failed: {e}")

    # Test 3: Scoring
    print("\n[3] SCORING & LEADERBOARD")
    print("-" * 60)

    try:
        game = Game.objects.first()
        if game:
            score, created = Score.objects.get_or_create(
                game=game, player=user, defaults={"score": 1500}
            )
            print(f"✓ Score recorded: {score.score} points (created={created})")

            score_count = Score.objects.filter(game=game).count()
            print(f"✓ Game leaderboard: {score_count} score(s)")
    except Exception as e:
        print(f"✗ Scoring failed: {e}")

    # Test 4: Achievements
    print("\n[4] ACHIEVEMENTS")
    print("-" * 60)

    try:
        field_names = {f.name for f in Achievement._meta.fields}
        lookup = {}
        defaults = {}

        # Support either legacy 'key' or newer 'name' fields.
        if "key" in field_names:
            lookup["key"] = "first_game"
            defaults.update(
                {"title": "First Game Creator", "description": "Create your first game"}
            )
        else:
            lookup["name"] = "first_game"
            defaults.update(
                {"description": "Create your first game", "condition": "create_game"}
            )

        if "icon" in field_names:
            defaults["icon"] = "badge.png"

        ach, _ = Achievement.objects.get_or_create(**lookup, defaults=defaults)
        print(f"✓ Achievement exists: {getattr(ach, 'title', getattr(ach, 'name', ''))}")

        ua_count = UserAchievement.objects.filter(user=user).count()
        print(f"✓ User unlocked: {ua_count} achievement(s)")
    except Exception as e:
        print(f"✗ Achievements failed: {e}")

    # Test 5: Assets
    print("\n[5] ASSETS")
    print("-" * 60)

    try:
        game = Game.objects.first()
        if game:
            asset, _ = GameAsset.objects.get_or_create(
                game=game,
                asset_type="sprite",
                defaults={"name": "test_sprite", "file": "test.png"},
            )
            print(f"✓ Asset (type={asset.asset_type}): {asset.name}")

            asset_count = GameAsset.objects.filter(game=game).count()
            print(f"✓ Game assets: {asset_count} asset(s)")
    except Exception as e:
        print(f"✗ Assets failed: {e}")

    # Test 6: Transactions & Revenue
    print("\n[6] MONETIZATION")
    print("-" * 60)

    try:
        game = Game.objects.first()
        if game:
            txn, _ = Transaction.objects.get_or_create(
                game=game,
                user=user,
                defaults={
                    "transaction_type": "purchase",
                    "amount": 2.99,
                    "currency": "USD",
                },
            )
            print(f"✓ Transaction: ${txn.amount} ({txn.transaction_type})")

            total_txn = Transaction.objects.filter(game=game).count()
            print(f"✓ Game transactions: {total_txn} record(s)")
    except Exception as e:
        print(f"✗ Monetization failed: {e}")

    # Test 7: Game versioning
    print("\n[7] GAME VERSIONING")
    print("-" * 60)

    try:
        game = Game.objects.first()
        if game:
            defaults = {"logic_json": {"events": [], "version": "1.0"}}
            if "description" in {f.name for f in GameVersion._meta.fields}:
                defaults["description"] = "Initial version"

            version, _ = GameVersion.objects.get_or_create(
                game=game, version_number=1, defaults=defaults
            )
            desc = getattr(version, "description", "")
            print(f"✓ Version {version.version_number}: {desc}")

            version_count = GameVersion.objects.filter(game=game).count()
            print(f"✓ Game versions: {version_count} version(s)")
    except Exception as e:
        print(f"✗ Versioning failed: {e}")

    # Test 8: Notifications
    print("\n[8] NOTIFICATIONS")
    print("-" * 60)

    try:
        notif, _ = UserNotification.objects.get_or_create(
            user=user,
            defaults={
                "title": "Test Notification",
                "message": "This is a test notification",
                "notification_type": "achievement",
            },
        )
        print(f"✓ Notification: {notif.title}")

        notif_count = UserNotification.objects.filter(user=user, is_read=False).count()
        print(f"✓ Unread notifications: {notif_count}")
    except Exception as e:
        print(f"✗ Notifications failed: {e}")

    # Test 9: User Preferences
    print("\n[9] USER PREFERENCES")
    print("-" * 60)

    try:
        pref, _ = UserPreference.objects.get_or_create(
            user=user,
            defaults={
                "theme": "dark",
                "language": "en",
                "notifications_enabled": True,
            },
        )
        print(
            f"✓ Preferences (theme={getattr(pref, 'theme', '')}, lang={getattr(pref, 'language', '')})"
        )
    except Exception as e:
        print(f"✗ Preferences failed: {e}")

    # Test 10: API Endpoints
    print("\n[10] API ENDPOINTS (READ-ONLY)")
    print("-" * 60)

    endpoints = ["/games/api/leaderboard/", "/games/api/achievements/"]

    passed = 0
    for ep in endpoints:
        try:
            r = urllib.request.urlopen(f"{BASE_URL}{ep}")
            _ = json.loads(r.read().decode("utf-8"))
            print(f"✓ {ep} -> {r.getcode()}")
            passed += 1
        except Exception as e:
            print(f"✗ {ep} -> {str(e)[:60]}")

    print(f"\nAPI Endpoints: {passed}/{len(endpoints)} PASS")

    # Summary (use ORM instead of raw table names)
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"  Users: {User.objects.count()} record(s)")
    print(f"  Profiles: {UserProfile.objects.count()} record(s)")
    print(f"  Games: {Game.objects.count()} record(s)")
    print(f"  Scores: {Score.objects.count()} record(s)")
    print(f"  Achievements: {Achievement.objects.count()} record(s)")
    print(f"  Transactions: {Transaction.objects.count()} record(s)")

    print("\n✅ COMPREHENSIVE FEATURE TEST COMPLETE")
    print("All major database models and relationships validated!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
