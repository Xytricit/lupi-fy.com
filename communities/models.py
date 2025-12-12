from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Community(models.Model):
    CATEGORY_CHOICES = [
        ("technology", "Technology"),
        ("design", "Design"),
        ("business", "Business"),
        ("lifestyle", "Lifestyle"),
        ("gaming", "Gaming"),
        ("photography", "Photography"),
        ("writing", "Writing"),
        ("music", "Music"),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_communities"
    )
    members = models.ManyToManyField(
        User, blank=True, related_name="joined_communities"
    )
    banner_image = models.ImageField(
        upload_to="community_banners/", blank=True, null=True
    )
    community_image = models.ImageField(
        upload_to="community_images/", blank=True, null=True
    )
    rules = models.TextField(blank=True)
    weekly_visits = models.IntegerField(default=0)
    weekly_contributions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "name"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if not self.banner_image:
            raise ValidationError({"banner_image": "A banner image is required."})
        if not self.community_image:
            raise ValidationError({"community_image": "A profile picture is required."})

    def __str__(self):
        return self.name


class CommunityPost(models.Model):
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="posts"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="community_posts"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    likes = models.ManyToManyField(
        User, related_name="liked_community_posts", blank=True
    )
    dislikes = models.ManyToManyField(
        User, related_name="disliked_community_posts", blank=True
    )
    bookmarks = models.ManyToManyField(
        User, related_name="bookmarked_community_posts", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.community.name})"


class CommunityPostComment(models.Model):
    post = models.ForeignKey(
        CommunityPost, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="community_post_comments"
    )
    text = models.TextField()
    likes = models.ManyToManyField(
        User, related_name="liked_community_post_comments", blank=True
    )
    dislikes = models.ManyToManyField(
        User, related_name="disliked_community_post_comments", blank=True
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


class ModerationReport(models.Model):
    REPORT_TYPES = [
        ("spam", "Spam"),
        ("harassment", "Harassment"),
        ("inappropriate", "Inappropriate Content"),
        ("misinformation", "Misinformation"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
    )
    comment = models.ForeignKey(
        CommunityPostComment,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
    )
    reported_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reports_made"
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.post:
            return f"Report on post {self.post.id} - {self.status}"
        return f"Report on comment {self.comment.id} - {self.status}"
