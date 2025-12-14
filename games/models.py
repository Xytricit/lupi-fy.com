from django.db import models
from django.conf import settings
import uuid


class Game(models.Model):
    """Minimal Game model used by tests as a placeholder."""

    VISIBILITY_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='games_owned', null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='games_created')
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='game_thumbnails/%Y/%m/%d/', null=True, blank=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='draft')
    monetization_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_games'
    )

    def __str__(self):
        return self.title


class GameAsset(models.Model):
    """Asset (sprite, sound, background) for a game."""
    
    ASSET_TYPES = [
        ('sprite', 'Sprite'),
        ('sound', 'Sound'),
        ('background', 'Background'),
        ('animation', 'Animation'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    file = models.FileField(upload_to='game_assets/%Y/%m/%d/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/', null=True, blank=True)
    metadata = models.JSONField(default=dict)  # width, height, duration, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('game', 'name')
    
    def __str__(self):
        return f"{self.game.title} - {self.name}"


class GameVersion(models.Model):
    """Version/snapshot of a game."""
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    logic_json = models.JSONField(default=dict)
    bundle_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('game', 'version_number')
    
    def __str__(self):
        return f"{self.game.title} v{self.version_number}"


class Score(models.Model):
    """Player score for a game."""
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='scores')
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.FloatField()
    metadata = models.JSONField(default=dict)  # custom game-specific data
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-value', '-created_at']
    
    def __str__(self):
        return f"{self.game.title} - {self.player}: {self.value}"


class Achievement(models.Model):
    """Badge/achievement definition."""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/')
    condition = models.CharField(max_length=200)  # e.g., "score_over_1000"
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Achievement earned by a user."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements_earned')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'achievement', 'game')
    
    def __str__(self):
        return f"{self.user} earned {self.achievement}"


class Transaction(models.Model):
    """Monetization transaction."""
    
    TRANSACTION_TYPES = [
        ('ad_revenue', 'Ad Revenue'),
        ('purchase', 'Purchase'),
        ('payout', 'Payout'),
        ('premium_unlock', 'Premium Unlock'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.transaction_type} ${self.amount}"

