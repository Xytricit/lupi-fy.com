from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import random

# -------------------------------
# Utility
# -------------------------------
def random_color():
    colors = [
        "#1f9cee", "#fec76f", "#ef4444", "#3b82f6",
        "#10b981", "#8b5cf6", "#f59e0b"
    ]
    return random.choice(colors)

# -------------------------------
# Custom User
# -------------------------------
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    color = models.CharField(max_length=20, default=random_color)
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    social_youtube = models.URLField(max_length=255, blank=True, null=True)
    social_instagram = models.URLField(max_length=255, blank=True, null=True)
    social_tiktok = models.URLField(max_length=255, blank=True, null=True)
    social_twitch = models.URLField(max_length=255, blank=True, null=True)
    social_github = models.URLField(max_length=255, blank=True, null=True)
    public_profile = models.BooleanField(default=True)
    warning_count = models.IntegerField(default=0)
    suspended_until = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    followers = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="following",
        blank=True
    )
    saved_communities = models.ManyToManyField(
        "communities.Community",
        related_name="saved_by_users",
        blank=True
    )

    def __str__(self):
        return self.username

    # -------------------------------
    # Helper methods for subscriptions
    # -------------------------------
    def subscribe_to_community(self, community):
        """Join a community and create a subscription if it doesn't exist."""
        if self not in community.members.all():
            community.members.add(self)
        Subscription.objects.get_or_create(user=self, community=community)

    def follow_author(self, author):
        """Follow an author and create a subscription if it doesn't exist."""
        if self not in author.followers.all():
            author.followers.add(self)
        Subscription.objects.get_or_create(user=self, author=author)

# -------------------------------
# Moderation Report
# -------------------------------
class ModerationReport(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post_content = models.TextField()
    banned_words_found = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report for {self.user.username} at {self.timestamp}"

# -------------------------------
# Subscription
# -------------------------------
class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        related_name="subscribers",
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_subscribers",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.community and not self.author:
            raise ValidationError("Subscription must have either a community or an author.")
        if self.community and self.author:
            raise ValidationError("Subscription can’t have both community and author.")

    def __str__(self):
        if self.community:
            return f"{self.user.username} subscribed to community {self.community.name}"
        if self.author:
            return f"{self.user.username} subscribed to author {self.author.username}"
        return f"{self.user.username} subscription"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "community"],
                name="unique_user_community",
                condition=models.Q(community__isnull=False)
            ),
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author",
                condition=models.Q(author__isnull=False)
            ),
        ]
        ordering = ["-created_at"]
