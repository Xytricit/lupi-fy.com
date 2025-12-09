from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Community(models.Model):
    CATEGORY_CHOICES = [
        ('technology', 'Technology'),
        ('design', 'Design'),
        ('business', 'Business'),
        ('lifestyle', 'Lifestyle'),
        ('gaming', 'Gaming'),
        ('photography', 'Photography'),
        ('writing', 'Writing'),
        ('music', 'Music'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_communities')
    members = models.ManyToManyField(User, blank=True, related_name='joined_communities')
    banner_image = models.ImageField(upload_to='community_banners/', blank=True, null=True)
    community_image = models.ImageField(upload_to='community_images/', blank=True, null=True)
    rules = models.TextField(blank=True)
    weekly_visits = models.IntegerField(default=0)
    weekly_contributions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.banner_image:
            raise ValidationError({'banner_image': "A banner image is required."})
        if not self.community_image:
            raise ValidationError({'community_image': "A profile picture is required."})

    def __str__(self):
        return self.name


class CommunityPost(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.community.name})"
