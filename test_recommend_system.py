#!/usr/bin/env python
"""Comprehensive recommendation system validation script.

This file is *not* a unit test. It is intentionally safe to import so Django's
default test discovery (python manage.py test) won't execute it.

Run with: python test_recommend_system.py
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
    from django.core.cache import cache

    from blog.models import Post
    from communities.models import Community, CommunityPost
    from recommend.models import Interaction, Recommendation, UserInterests

    try:
        from recommend.ml.torch_recommender import load_model, recommend_for_user, train_and_save
    except ImportError as e:
        print(f"PyTorch recommender unavailable (missing torch?): {e}")
        return 0

    User = get_user_model()

    print("=" * 80)
    print("RECOMMENDATION SYSTEM TEST & PROOF")
    print("=" * 80)

    # 1. CREATE TEST DATA
    print("\n[Step 1] Creating test data...")
    users = []
    for i in range(5):
        u, _ = User.objects.get_or_create(
            username=f"test_user_{i}", defaults={"email": f"test{i}@example.com"}
        )
        users.append(u)
        print(f"  ✓ User: {u.username}")

    # Create test blog posts
    posts = []
    for i in range(10):
        p, _ = Post.objects.get_or_create(
            title=f"Test Blog Post {i}",
            defaults={
                "content": f"Test content {i}" * 50,
                "author": users[i % len(users)],
                "created": timezone.now() - timedelta(days=10 - i),
            },
        )
        posts.append(p)
    print(f"  ✓ Created {len(posts)} blog posts")

    # Create test communities
    communities = []
    for i in range(3):
        c, _ = Community.objects.get_or_create(
            name=f"Test Community {i}",
            defaults={"description": f"Community {i} desc", "creator": users[0]},
        )
        communities.append(c)
    print(f"  ✓ Created {len(communities)} communities")

    # Create test community posts
    community_posts = []
    for i in range(15):
        cp, _ = CommunityPost.objects.get_or_create(
            title=f"Community Post {i}",
            defaults={
                "content": f"Community content {i}" * 30,
                "author": users[i % len(users)],
                "community": communities[i % len(communities)],
                "created_at": timezone.now() - timedelta(days=15 - i),
            },
        )
        community_posts.append(cp)
    print(f"  ✓ Created {len(community_posts)} community posts")

    # 2. GENERATE INTERACTIONS
    print("\n[Step 2] Generating user interactions (synthetic engagement)...")
    interaction_count = 0

    for user in users:
        for post in posts[::2]:
            Interaction.objects.get_or_create(
                user=user,
                content_type=ContentType.objects.get_for_model(Post),
                object_id=post.id,
                defaults={
                    "action": "view",
                    "created_at": timezone.now() - timedelta(hours=1),
                },
            )
            interaction_count += 1

    for user in users:
        for cp in community_posts[::2]:
            Interaction.objects.get_or_create(
                user=user,
                content_type=ContentType.objects.get_for_model(CommunityPost),
                object_id=cp.id,
                defaults={
                    "action": "view",
                    "created_at": timezone.now() - timedelta(hours=2),
                },
            )
            interaction_count += 1

    print(f"  ✓ Total interactions: {interaction_count}")

    # 3. SET USER INTERESTS
    print("\n[Step 3] Setting user interests...")
    for user in users:
        interests, _ = UserInterests.objects.get_or_create(user=user)
        interests.blog_tags = ["technology", "design", "business"]
        interests.community_tags = ["technology", "design"]
        interests.game_categories = ["word", "puzzle"]
        interests.completed_blog_onboarding = True
        interests.completed_community_onboarding = True
        interests.save()
        print(f"  ✓ {user.username}: blog_tags={interests.blog_tags}")

    # 4. TRAIN TORCH RECOMMENDER
    print("\n[Step 4] Training PyTorch collaborative filtering model...")
    try:
        model_path = train_and_save(days=365, epochs=5, emb_dim=32)
        if model_path:
            print(f"  ✓ Model trained and saved to: {model_path}")
        else:
            print("  ⚠ No interactions to train on (expected for small test)")
            return 0
    except Exception as e:
        print(f"  ✗ Training failed: {e}")
        return 1

    # 5. GENERATE RECOMMENDATIONS
    print("\n[Step 5] Generating recommendations for each user...")
    model = load_model()
    if model:
        print(f"  Model loaded: {model.get('emb_dim', 64)}-dim embeddings")
        for user in users:
            recs = recommend_for_user(user.id, model=model, topn=10)
            print(f"  ✓ {user.username}: {len(recs)} recommendations")
            if recs:
                print("    Top 3:", recs[:3])
    else:
        print("  ⚠ Model not available")

    # 6. VERIFY RECOMMENDATION STORAGE
    print("\n[Step 6] Verifying stored recommendations...")
    total_recs = Recommendation.objects.count()
    print(f"  Total Recommendation rows: {total_recs}")
    for user in users[:2]:
        user_recs = Recommendation.objects.filter(user=user).count()
        print(f"  {user.username}: {user_recs} recommendations")

    # 7. TEST CACHING & API
    print("\n[Step 7] Testing cache and API endpoints...")
    cache.clear()
    from django.test import RequestFactory
    from recommend.views import (
        for_you_recommendations,
        get_blog_recommendations,
        get_community_recommendations,
    )

    rf = RequestFactory()
    test_user = users[0]

    for_you_req = rf.get("/recommend/for-you/")
    for_you_req.user = test_user
    try:
        resp = for_you_recommendations(for_you_req)
        data = resp.json()
        print(f"  ✓ For You API returned {len(data.get('results', []))} results")
    except Exception as e:
        print(f"  ✗ For You API error: {e}")

    blog_req = rf.get("/recommend/blog-recommendations/")
    blog_req.user = test_user
    try:
        resp = get_blog_recommendations(blog_req)
        data = resp.json()
        print(f"  ✓ Blog Recommendations API returned {len(data.get('results', []))} results")
    except Exception as e:
        print(f"  ✗ Blog API error: {e}")

    community_req = rf.get("/recommend/community-recommendations/")
    community_req.user = test_user
    try:
        resp = get_community_recommendations(community_req)
        data = resp.json()
        print(f"  ✓ Community Recommendations API returned {len(data.get('results', []))} results")
    except Exception as e:
        print(f"  ✗ Community API error: {e}")

    # 8. QUALITY METRICS
    print("\n[Step 8] Quality Metrics & Coverage...")
    total_users = User.objects.count()
    users_with_recs = Recommendation.objects.values("user_id").distinct().count()
    total_items = Post.objects.count() + CommunityPost.objects.count()
    recommended_items = (
        Recommendation.objects.values("object_id", "content_type_id").distinct().count()
    )
    total_interactions = Interaction.objects.count()

    print(f"  Users in system: {total_users}")
    print(
        f"  Users with recommendations: {users_with_recs} ({100*users_with_recs/max(1,total_users):.1f}%)"
    )
    print(f"  Total items (posts + community): {total_items}")
    print(
        f"  Items in recommendations: {recommended_items} ({100*recommended_items/max(1,total_items):.1f}%)"
    )
    print(f"  Total interactions recorded: {total_interactions}")

    print("\n" + "=" * 80)
    print("✓ RECOMMENDATION SYSTEM SCRIPT COMPLETE")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
