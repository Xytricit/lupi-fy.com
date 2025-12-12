import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client

from blog.models import ModerationReport, Post


class Command(BaseCommand):
    help = "Test report post via test client"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(username="Turbo").first() or User.objects.first()
        post = Post.objects.first()
        print("Using user:", user and user.username, "post id:", post.id)
        client = Client()
        client.force_login(user)
        res = client.post(
            f"/posts/post/{post.id}/report/",
            data=json.dumps({"reason": "spam", "details": "test-run"}),
            content_type="application/json",
        )
        print("status code:", res.status_code)
        print("response:", res.content)
        latest = ModerationReport.objects.order_by("-timestamp").first()
        print(
            "latest report id:",
            latest.id,
            "post_id:",
            latest.post_id,
            "user:",
            latest.user.username,
        )
