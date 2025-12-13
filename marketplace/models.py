from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal
import uuid
import os


# ============================================================================
# PROJECT MODEL - Core marketplace listing
# ============================================================================
class Project(models.Model):
    """
    Sellable project created by creators.
    
    INTEGRATION POINTS:
    - creator: FK to CustomUser (accounts.models.CustomUser)
    - project_id: Links to projects by UUID (flexible for any creator work)
    """
    
    # Core Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marketplace_projects'
    )
    
    # Link to existing content (game, tool, template, etc)
    project_id = models.UUIDField(
        null=True, 
        blank=True,
        db_column='game_id',  # Use existing database column name
        help_text="UUID of the associated content from other apps"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    is_free = models.BooleanField(default=False)
    
    # Content
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    thumbnail = models.ImageField(
        upload_to='marketplace/thumbnails/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])]
    )
    
    # Project Files
    project_file = models.FileField(
        upload_to='marketplace/projects/%Y/%m/',
        validators=[FileExtensionValidator(['zip'])],
        help_text="Project bundle from creator"
    )
    file_size = models.BigIntegerField(default=0)
    
    # Metadata
    version = models.CharField(max_length=20, default='1.0.0')
    category = models.CharField(max_length=50, choices=[
        ('action', 'Action'),
        ('puzzle', 'Puzzle'),
        ('strategy', 'Strategy'),
        ('arcade', 'Arcade'),
        ('adventure', 'Adventure'),
        ('educational', 'Educational'),
        ('template', 'Template'),
        ('asset_pack', 'Asset Pack'),
    ])
    tags = models.JSONField(default=list)
    
    # Status & Approval
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    rejection_reason = models.TextField(blank=True, null=True)
    
    # Statistics
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    rating_average = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MinValueValidator(5)]
    )
    rating_count = models.PositiveIntegerField(default=0)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Featured/Trending
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-sales_count']),
            models.Index(fields=['-rating_average']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} by {self.creator.username}"
    
    def get_absolute_url(self):
        return f"/marketplace/{self.slug}/"
    
    def increment_view(self):
        """Call when project page is viewed"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def can_download(self, user):
        """Check if user has purchased or project is free"""
        if self.is_free:
            return True
        return Purchase.objects.filter(
            project=self,
            buyer=user,
            status='completed'
        ).exists()


# ============================================================================
# PROJECT MEDIA - Screenshots, videos, preview images
# ============================================================================
class ProjectMedia(models.Model):
    """Additional media for project listings (screenshots, preview images, videos)"""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='media_files'
    )
    
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(
        upload_to='marketplace/media/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'mp4', 'gif'])]
    )
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.project.title} - {self.media_type}"


# ============================================================================
# PURCHASE MODEL - Track sales and access
# ============================================================================
class Purchase(models.Model):
    """
    Records when a user purchases a project.
    
    INTEGRATION POINTS:
    - Creates download access record
    - Triggers notification to creator
    - Updates UserProfile.total_revenue (accounts/models_extended.py)
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='purchases'
    )
    
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    
    # Payment Info
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(max_length=20, choices=[
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('free', 'Free'),
    ])
    transaction_id = models.CharField(max_length=255, blank=True)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Revenue Split
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creator_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Refund info
    refund_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', '-created_at']),
            models.Index(fields=['project', '-created_at']),
        ]
        unique_together = [['project', 'buyer']]
    
    def __str__(self):
        return f"{self.buyer.username} - {self.project.title} (${self.price_paid})"
    
    def complete_purchase(self):
        """Mark purchase as completed and update stats"""
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            
            # Update project stats
            self.project.sales_count += 1
            self.project.save(update_fields=['sales_count'])
            
            # Create download access
            DownloadAccess.objects.create(
                purchase=self,
                project=self.project,
                user=self.buyer
            )


# ============================================================================
# DOWNLOAD ACCESS - Secure download management
# ============================================================================
class DownloadAccess(models.Model):
    """Tracks download permissions and generates secure download links"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='download_access'
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Download Tracking
    download_count = models.PositiveIntegerField(default=0)
    last_download_at = models.DateTimeField(null=True, blank=True)
    
    # Access Control
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['project', 'user']]
    
    def __str__(self):
        return f"{self.user.username} - {self.project.title}"
    
    def can_download(self):
        """Check if user can download (not expired, active)"""
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


# ============================================================================
# REVIEW/RATING SYSTEM
# ============================================================================
class ProjectReview(models.Model):
    """User reviews and ratings for purchased projects"""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='marketplace_reviews'
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        null=True
    )
    
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MinValueValidator(5)]
    )
    title = models.CharField(max_length=100)
    content = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    
    # Creator response
    creator_response = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['project', 'reviewer']]
    
    def __str__(self):
        return f"{self.reviewer.username} - {self.project.title} ({self.rating}★)"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_project_rating()
    
    def update_project_rating(self):
        """Recalculate project's average rating"""
        from django.db.models import Avg, Count
        result = ProjectReview.objects.filter(
            project=self.project,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            count=Count('id')
        )
        self.project.rating_average = result['avg_rating'] or 0
        self.project.rating_count = result['count']
        self.project.save(update_fields=['rating_average', 'rating_count'])


# ============================================================================
# WISHLIST - User saved projects
# ============================================================================
class Wishlist(models.Model):
    """User's wishlist/saved projects"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['user', 'project']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.title}"


# ============================================================================
# ANALYTICS - Track marketplace performance
# ============================================================================
class ProjectAnalytics(models.Model):
    """Daily analytics snapshot for projects"""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    date = models.DateField(default=timezone.now)
    
    # Daily metrics
    views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    sales = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Traffic sources
    traffic_sources = models.JSONField(default=dict)
    
    class Meta:
        unique_together = [['project', 'date']]
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.project.title} - {self.date}"


# ============================================================================
# PAYOUT - Creator earnings management
# ============================================================================
class CreatorPayout(models.Model):
    """Track creator earnings and payout requests"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payouts'
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    payout_method = models.CharField(max_length=20, choices=[
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
    ])
    payout_email = models.EmailField()
    transaction_id = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.creator.username} - ${self.amount} ({self.status})"


# ============================================================================
# AI TAG SUGGESTIONS - For project categorization
# ============================================================================
class AITagSuggestion(models.Model):
    """AI-generated tag suggestions for projects"""
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='ai_tag_suggestions'
    )
    
    suggested_tags = models.JSONField(default=list)
    confidence_scores = models.JSONField(default=dict)
    
    applied = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.project.title} - AI Tags"
