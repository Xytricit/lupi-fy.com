from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model


# ------------------------
# Tag & Category Models
# ------------------------
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# ------------------------
# PostImage Model
# ------------------------
class PostImage(models.Model):
    image = models.ImageField(upload_to="post_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"


# ------------------------
# Post Model
# ------------------------
class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    description = models.TextField(max_length=500, default="No description yet")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    images = models.ManyToManyField(PostImage, blank=True)

    # Social interactions
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="disliked_posts", blank=True
    )
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="bookmarked_posts", blank=True
    )
    # View counter (increments each time a post detail is opened)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


# ------------------------
# Comment Model
# ------------------------
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )

    # Social interactions
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_comments", blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="disliked_comments", blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"


# ------------------------
# Moderation Report Model
# ------------------------
class ModerationReport(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="moderation_reports",
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="reports", null=True, blank=True
    )
    post_content = models.TextField()
    banned_words_found = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.user} at {self.timestamp}"


# ------------------------
# Add followers to User
# ------------------------
User = get_user_model()

if not hasattr(User, "followers"):
    User.add_to_class(
        "followers",
        models.ManyToManyField(
            "self", symmetrical=False, related_name="following", blank=True
        ),
    )
