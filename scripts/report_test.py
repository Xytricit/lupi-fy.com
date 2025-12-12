from django.contrib.auth import get_user_model
from django.test import Client
import json

from blog.models import ModerationReport, Post

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
