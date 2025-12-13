from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    """Extended user profile with roles and game creation stats"""
    ROLE_CHOICES = (
        ('player', 'Player'),
        ('developer', 'Developer'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='player')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    games_created = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

class UserNotification(models.Model):
    """In-app notifications for game reviews, achievements, etc."""
    NOTIFICATION_TYPES = (
        ('game_approved', 'Game Approved'),
        ('game_rejected', 'Game Rejected'),
        ('achievement_earned', 'Achievement Earned'),
        ('follower_created_game', 'Follower Created Game'),
        ('leaderboard_rank', 'Leaderboard Rank'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_game = models.ForeignKey('games.Game', null=True, blank=True, on_delete=models.SET_NULL)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

class UserPreference(models.Model):
    """User settings and preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    email_notifications = models.BooleanField(default=True)
    show_profile_public = models.BooleanField(default=True)
    allow_game_remixes = models.BooleanField(default=True)
    preferred_theme = models.CharField(max_length=20, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"
