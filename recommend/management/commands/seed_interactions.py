import random

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import Post

try:
    from communities.models import CommunityPost
except Exception:
    CommunityPost = None

from recommend.models import Interaction


class Command(BaseCommand):
    help = "Seed synthetic Interaction rows from existing posts and community posts for training/testing."

    def add_arguments(self, parser):
        parser.add_argument("--per-user-posts", type=int, default=6)
        parser.add_argument("--per-user-community", type=int, default=4)

    def handle(self, *args, **options):
        User = get_user_model()
        users = list(User.objects.all())
        posts = list(Post.objects.all())
        cposts = list(CommunityPost.objects.all()) if CommunityPost else []
        if not users:
            self.stderr.write("No users to seed interactions for.")
            return
        if not posts and not cposts:
            self.stderr.write(
                "No posts or community posts found to seed interactions from."
            )
            return

        created = 0
        for user in users:
            # sample posts
            sample_posts = (
                random.sample(posts, min(len(posts), options["per_user_posts"]))
                if posts
                else []
            )
            for p in sample_posts:
                ct = ContentType.objects.get_for_model(p)
                Interaction.objects.create(
                    user=user, content_type=ct, object_id=p.id, value=1.0
                )
                created += 1
            # sample community posts
            sample_c = (
                random.sample(cposts, min(len(cposts), options["per_user_community"]))
                if cposts
                else []
            )
            for cp in sample_c:
                ct = ContentType.objects.get_for_model(cp)
                Interaction.objects.create(
                    user=user, content_type=ct, object_id=cp.id, value=1.0
                )
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created} synthetic interactions for {len(users)} users"
            )
        )
