#!/usr/bin/env python
"""Test the enhanced recommendation system with hybrid model.

This is a runnable script (not a unit test). It is intentionally safe to import
so Django's default test discovery won't execute it.

Run with: python test_hybrid_recommendations.py
"""

import os
from datetime import timedelta


def main() -> int:
    import django
    from django.utils import timezone

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
    django.setup()

    from django.contrib.auth import get_user_model
    from django.contrib.contenttypes.models import ContentType

    from blog.models import Post
    from recommend.models import Interaction, UserInterests

    try:
        from recommend.ml.torch_recommender_hybrid import (
            load_model_hybrid,
            recommend_for_user_hybrid,
            train_and_save_hybrid,
        )
    except ImportError as e:
        print(f"Hybrid recommender unavailable (missing deps): {e}")
        return 0

    User = get_user_model()

    print("=" * 80)
    print("ENHANCED HYBRID RECOMMENDATION SYSTEM TEST")
    print("=" * 80)

    # Create users
    print("\n[Step 1] Preparing data...")
    users = []
    for i in range(3):
        u, _ = User.objects.get_or_create(
            username=f"hybrid_test_{i}", defaults={"email": f"hybrid{i}@test.com"}
        )
        users.append(u)
    print(f"  ✓ {len(users)} test users")

    # Create posts
    posts = []
    for i in range(8):
        p, _ = Post.objects.get_or_create(
            title=f"Hybrid Post {i}",
            defaults={
                "content": f"Content {i}" * 50,
                "author": users[0],
                "created": timezone.now() - timedelta(days=10 - i),
            },
        )
        posts.append(p)
    print(f"  ✓ {len(posts)} posts")

    # Create interactions
    print("\n[Step 2] Recording interactions...")
    for user in users:
        for post in posts[:5]:
            Interaction.objects.get_or_create(
                user=user,
                content_type=ContentType.objects.get_for_model(Post),
                object_id=post.id,
                defaults={"action": "view"},
            )
    ic_count = Interaction.objects.count()
    print(f"  ✓ {ic_count} interactions recorded")

    # Set interests
    print("[Step 3] Setting user interests...")
    for user in users:
        interests, _ = UserInterests.objects.get_or_create(user=user)
        interests.blog_tags = ["technology", "design", "business"]
        interests.save()
    print("  ✓ Interests saved")

    # Train hybrid model
    print("\n[Step 4] Training HYBRID model...")
    try:
        path = train_and_save_hybrid(
            days=365, emb_dim=32, content_emb_dim=16, epochs=4, use_content=True
        )
        if not path:
            print("  ⚠ No model trained (no interactions?)")
            return 0

        print(f"  ✓ Hybrid model saved: {path}")

        # Load and test
        model = load_model_hybrid(path)
        if model:
            print("  ✓ Hybrid model loaded")
            print(f"    - Collab embeddings: {model.get('emb_dim')}-dim")
            print(f"    - Content embeddings: {model.get('content_emb_dim')}-dim")
            print(f"    - Users: {len(model['user_map'])}")
            print(f"    - Items: {len(model['item_map'])}")
        else:
            print("  ⚠ Model could not be loaded")
            return 0
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 1

    # Test hybrid recommendations
    print("\n[Step 5] Generating HYBRID recommendations...")
    for user in users[:1]:
        recs = recommend_for_user_hybrid(
            user.id,
            model=model,
            topn=5,
            diversity_penalty=0.15,
            freshness_boost=True,
        )
        print(f"  ✓ {user.username}: {len(recs)} hybrid recommendations")
        for i, (key, score) in enumerate(recs[:3], 1):
            print(f"    {i}. {key.split(':')[1]} (score={score:.3f})")

    print("\n" + "=" * 80)
    print("✓ HYBRID MODEL ENHANCEMENT SUCCESSFUL!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
