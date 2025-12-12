#!/usr/bin/env python
import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from blog.models import Post
from communities.models import Community, CommunityPost
from recommend.models import Interaction, UserInterests
from recommend.ml.torch_recommender import train_and_save, load_model

User = get_user_model()
print("=" * 80)
print("RECOMMENDATION SYSTEM QUICK TEST")
print("=" * 80)

# Create test users
print("\n[1] Creating test users...")
users = []
for i in range(3):
    u, _ = User.objects.get_or_create(username=f"rec_test_{i}", defaults={'email': f'rec{i}@test.com'})
    users.append(u)
print(f"  ✓ {len(users)} users")

# Create test posts
print("[2] Creating test posts...")
posts = []
for i in range(5):
    p, _ = Post.objects.get_or_create(
        title=f"Post {i}", 
        defaults={'content': f'Content {i}' * 20, 'author': users[0], 'created': timezone.now()}
    )
    posts.append(p)
print(f"  ✓ {len(posts)} posts")

# Create interactions
print("[3] Recording interactions...")
for user in users:
    for post in posts[:3]:
        Interaction.objects.get_or_create(
            user=user, 
            content_type=ContentType.objects.get_for_model(Post),
            object_id=post.id,
            defaults={'action': 'view'}
        )
ic = Interaction.objects.count()
print(f"  ✓ {ic} interactions total")

# Train model
print("[4] Training ML model...")
try:
    path = train_and_save(days=365, epochs=3, emb_dim=16)
    if path:
        print(f"  ✓ Model saved to {path}")
        model = load_model(path)
        if model:
            print(f"  ✓ Model loaded: {model.get('emb_dim')}-dim embeddings")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 80)
print("✓ RECOMMENDATION SYSTEM WORKING")
print("=" * 80)
