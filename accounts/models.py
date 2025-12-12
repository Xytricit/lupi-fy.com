import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


# -------------------------------
# Utility
# -------------------------------
def random_color():
    colors = [
        "#1f9cee",
        "#fec76f",
        "#ef4444",
        "#3b82f6",
        "#10b981",
        "#8b5cf6",
        "#f59e0b",
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
    is_email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    email_verification_attempts = models.IntegerField(default=0)
    email_verification_expires_at = models.DateTimeField(null=True, blank=True)
    social_youtube = models.URLField(max_length=255, blank=True, null=True)
    social_instagram = models.URLField(max_length=255, blank=True, null=True)
    social_tiktok = models.URLField(max_length=255, blank=True, null=True)
    social_twitch = models.URLField(max_length=255, blank=True, null=True)
    social_github = models.URLField(max_length=255, blank=True, null=True)
    # Controls whether the user's profile/username can appear in public searches
    # Default changed to False to opt users out by default.
    public_profile = models.BooleanField(default=False)
    allow_public_socials = models.BooleanField(default=True)
    # Whether this user accepts direct messages from other users
    allow_dms = models.BooleanField(default=True)
    # Users this user has blocked (they cannot message this user; their messages are hidden)
    blocked_users = models.ManyToManyField(
        "self", symmetrical=False, related_name="blocked_by", blank=True
    )
    warning_count = models.IntegerField(default=0)
    suspended_until = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
    )
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )
    saved_communities = models.ManyToManyField(
        "communities.Community", related_name="saved_by_users", blank=True
    )
    # Appearance preference: light/dark/system
    THEME_CHOICES = [("light", "Light"), ("dark", "Dark"), ("system", "System")]
    theme_preference = models.CharField(
        max_length=10, choices=THEME_CHOICES, default="light"
    )
    # User-selected accent color (hex) and base font size
    accent_color = models.CharField(max_length=9, default="#1f9cee")
    font_size = models.PositiveSmallIntegerField(default=14)

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
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions"
    )
    community = models.ForeignKey(
        "communities.Community",
        on_delete=models.CASCADE,
        related_name="subscribers",
        null=True,
        blank=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="author_subscribers",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.community and not self.author:
            raise ValidationError(
                "Subscription must have either a community or an author."
            )
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
                condition=models.Q(community__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author",
                condition=models.Q(author__isnull=False),
            ),
        ]
        ordering = ["-created_at"]


class DirectMessage(models.Model):
    """Model for direct messages between users"""

    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.sender.username} → {self.recipient.username}: {self.content[:30]}"
        )


class Conversation(models.Model):
    """Model to group messages between two users"""

    user1 = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="conversations_as_user1"
    )
    user2 = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="conversations_as_user2"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user1", "user2")
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Conversation: {self.user1.username} ↔ {self.user2.username}"


class GameLobbyBan(models.Model):
    """Model to track bans for the Try Not To Get Banned game"""

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="game_bans"
    )
    banned_until = models.DateTimeField()  # When the ban expires
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} banned until {self.banned_until}"

    def is_active(self):
        """Check if the ban is still active"""
        from django.utils import timezone

        return timezone.now() < self.banned_until


class Notification(models.Model):
    """Model for user notifications (admin warnings, post deletions, etc.)"""

    NOTIFICATION_TYPES = (
        ("admin_warning", "Admin Warning"),
        ("post_deleted", "Post Deleted"),
        ("comment_on_post", "Comment on Post"),
        ("user_mentioned", "User Mentioned"),
        ("follow", "New Follower"),
        ("message", "New Message"),
        ("other", "Other"),
    )

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default="other"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    related_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifs_about_me",
    )
    related_post = models.ForeignKey(
        "blog.Post", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class GameLobbyMessage(models.Model):
    """Persistent lobby messages for Try Not To Get Banned.

    Stores both user messages and system announcements so the lobby can
    show a history and broadcasts to all connected clients.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="lobby_messages",
        null=True,
        blank=True,
    )
    author_name = models.CharField(max_length=150, blank=True, null=True)
    content = models.TextField()
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        if self.is_system:
            return f"[SYSTEM] {self.content[:40]}"
        return f"{self.author_name or (self.user.username if self.user else 'Unknown')}: {self.content[:40]}"


class GameLobbyChallenge(models.Model):
    """Per-user 12-letter challenge shown under the lobby chat.

    `letters` is a list of 12 uppercase single-character strings. `used_letters`
    tracks which letters the user has 'ticked' by typing dictionary words that
    contain those letters. When all letters are used, `completed` is True.
    """

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="lobby_challenges"
    )
    letters = models.JSONField(default=list)  # list of 12 single-character letters
    used_letters = models.JSONField(default=list)  # list of letters already used
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def mark_letters(self, letters_to_mark):
        """Mark letters (list) as used; return newly marked letters."""
        newly = []
        for ch in letters_to_mark:
            chu = ch.upper()
            if chu in self.letters and chu not in self.used_letters:
                self.used_letters.append(chu)
                newly.append(chu)
        if newly:
            if set(self.used_letters) >= set(self.letters):
                self.completed = True
            self.save()
        return newly


class WordListGame(models.Model):
    """Full standalone word-list game for users.

    This tracks a user's active word list, used words, and score. Per-word
    points are 6; completion bonus is 50.
    """

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="word_list_games"
    )
    words = models.JSONField(default=list)
    used_words = models.JSONField(default=list)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def add_used_words(self, new_words):
        added = 0
        for w in new_words:
            if w not in self.used_words:
                self.used_words.append(w)
                self.score += 6
                added += 1
        # completion bonus
        if set(self.used_words) >= set(self.words) and self.words:
            self.score += 50
            # reset words and used_words to allow new game
            self.words = []
            self.used_words = []
        self.save()
        return added


class LetterSetGame(models.Model):
    """Model to track Letter Set game sessions"""

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="letter_set_games"
    )
    letters = models.CharField(max_length=15)  # 15 random letters from alphabet
    score = models.IntegerField(default=0)
    completed_words = models.TextField(
        default=""
    )  # Comma-separated list of completed words
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - Letters: {self.letters} - Score: {self.score}"

    def get_completed_words_list(self):
        """Get completed words as a list"""
        if not self.completed_words:
            return []
        return [w.strip() for w in self.completed_words.split(",") if w.strip()]

    def add_word(self, word):
        """Add a word to completed words if not already added"""
        words_list = self.get_completed_words_list()
        if word.lower() not in [w.lower() for w in words_list]:
            words_list.append(word)
            self.completed_words = ",".join(words_list)
            self.save()
            return True
        return False
