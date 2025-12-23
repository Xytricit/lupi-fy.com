from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Game categories for user preferences
GAME_CATEGORIES = [
    ("word", "Word Games"),
    ("puzzle", "Puzzle Games"),
    ("strategy", "Strategy Games"),
    ("casual", "Casual Games"),
    ("trivia", "Trivia"),
    ("educational", "Educational"),
]

# Blog post tags
BLOG_TAGS = [
    ("technology", "Technology"),
    ("design", "Design"),
    ("business", "Business"),
    ("lifestyle", "Lifestyle"),
    ("gaming", "Gaming"),
    ("photography", "Photography"),
    ("writing", "Writing"),
    ("music", "Music"),
    ("education", "Education"),
    ("science", "Science"),
    ("health", "Health & Fitness"),
    ("entertainment", "Entertainment"),
    ("art", "Art & Illustration"),
    ("finance", "Finance"),
    ("food", "Food"),
    ("travel", "Travel"),
    ("fashion", "Fashion & Beauty"),
    ("diy", "DIY & Making"),
    ("nature", "Nature"),
    ("history", "History & Culture"),
]

# Community tags (same as blog for now)
COMMUNITY_TAGS = BLOG_TAGS

ACTION_ENGAGEMENT_BASE_WEIGHTS = {
    "complete": 2.0,
    "play": 1.25,
    "like": 1.5,
    "dislike": 0.4,
    "skip": 0.3,
    "view": 0.8,
    "impression": 0.6,
    "click": 1.1,
}


class UserInterests(models.Model):
    """Track user interests across games, blog posts, and community content."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interests"
    )

    # Game interests
    game_categories = models.JSONField(
        default=list, blank=True
    )  # list of game category slugs

    # Blog post interests
    blog_tags = models.JSONField(default=list, blank=True)  # list of blog tag slugs

    # Community post interests
    community_tags = models.JSONField(
        default=list, blank=True
    )  # list of community tag slugs

    # Onboarding status flags
    completed_game_onboarding = models.BooleanField(default=False)
    completed_blog_onboarding = models.BooleanField(default=False)
    completed_community_onboarding = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "User Interests"

    def __str__(self):
        return f"{self.user.username} interests"

    # Backwards-compatible aliases for older API/tests
    @property
    def categories(self):
        return self.game_categories

    @categories.setter
    def categories(self, value):
        self.game_categories = value

    @property
    def completed_onboarding(self):
        return self.completed_game_onboarding

    @completed_onboarding.setter
    def completed_onboarding(self, value):
        self.completed_game_onboarding = value


class Interaction(models.Model):
    """Records that a user interacted with a game/content (play, like, view, complete)."""

    ACTION_CHOICES = [
        ("play", "Play"),
        ("like", "Like"),
        ("dislike", "Dislike"),
        ("view", "View"),
        ("complete", "Complete"),
        ("skip", "Skip"),
        ("impression", "Impression"),
        ("click", "Click"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default="play")
    value = models.FloatField(default=1.0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.action} {self.content_type_id}:{self.object_id}"

    def engagement_weight(self):
        weight = max(self.value or 0.5, 0.5)
        weight *= ACTION_ENGAGEMENT_BASE_WEIGHTS.get(self.action, 1.0)
        meta = self.metadata or {}
        duration = meta.get("duration_seconds") or meta.get("duration") or 0
        try:
            duration = float(duration)
        except (TypeError, ValueError):
            duration = 0.0
        scroll = meta.get("scroll_depth") or meta.get("scroll_fraction") or 0
        try:
            scroll = float(scroll)
        except (TypeError, ValueError):
            scroll = 0.0
        engagement_bonus = min(2.5, duration / 30.0) + min(1.0, scroll)
        if meta.get("bookmarked") or meta.get("saved") or meta.get("wishlisted"):
            engagement_bonus += 1.0
        if meta.get("liked"):
            engagement_bonus += 0.5
        return max(0.1, weight + engagement_bonus)


class Recommendation(models.Model):
    """Per-user precomputed recommendations."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-score"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"Rec {self.user_id} -> {self.content_type_id}:{self.object_id} ({self.score:.3f})"
