from django.contrib import admin
from .models import (
    Project, ProjectMedia, Purchase, DownloadAccess,
    ProjectReview, Wishlist, ProjectAnalytics, CreatorPayout,
    AITagSuggestion
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'price', 'status', 'sales_count', 'created_at']
    list_filter = ['status', 'category', 'is_featured', 'created_at']
    search_fields = ['title', 'creator__username', 'description']
    readonly_fields = ['views_count', 'downloads_count', 'sales_count', 'rating_average', 'rating_count', 'created_at', 'updated_at']
    actions = ['approve_projects', 'reject_projects']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'creator', 'category', 'version')
        }),
        ('Content', {
            'fields': ('description', 'short_description', 'thumbnail', 'tags')
        }),
        ('Pricing & Files', {
            'fields': ('price', 'is_free', 'project_file', 'file_size')
        }),
        ('Status & Approval', {
            'fields': ('status', 'rejection_reason', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views_count', 'downloads_count', 'sales_count', 'rating_average', 'rating_count'),
            'classes': ('collapse',)
        }),
        ('Featured', {
            'fields': ('is_featured', 'featured_until'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Content Link', {
            'fields': ('project_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_projects(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} projects approved')
    approve_projects.short_description = "Approve selected projects"
    
    def reject_projects(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} projects rejected')
    reject_projects.short_description = "Reject selected projects"


@admin.register(ProjectMedia)
class ProjectMediaAdmin(admin.ModelAdmin):
    list_display = ['project', 'media_type', 'created_at']
    list_filter = ['media_type', 'created_at']
    search_fields = ['project__title', 'caption']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'project', 'price_paid', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['buyer__username', 'project__title', 'transaction_id']
    readonly_fields = ['id', 'created_at', 'completed_at', 'refunded_at']
    
    fieldsets = (
        ('Transaction', {
            'fields': ('id', 'project', 'buyer', 'status')
        }),
        ('Payment', {
            'fields': ('price_paid', 'payment_method', 'transaction_id')
        }),
        ('Revenue Split', {
            'fields': ('platform_fee', 'creator_earnings')
        }),
        ('Refund Info', {
            'fields': ('refund_reason',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'refunded_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DownloadAccess)
class DownloadAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'download_count', 'is_active', 'last_download_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'project__title']
    readonly_fields = ['id', 'created_at']


@admin.register(ProjectReview)
class ProjectReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'project', 'rating', 'is_approved', 'is_flagged', 'created_at']
    list_filter = ['is_approved', 'is_flagged', 'rating', 'created_at']
    search_fields = ['reviewer__username', 'project__title', 'content']
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved')
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews rejected')
    reject_reviews.short_description = "Reject selected reviews"


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'project__title']


@admin.register(ProjectAnalytics)
class ProjectAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['project', 'date', 'views', 'downloads', 'sales', 'revenue']
    list_filter = ['date', 'project']
    search_fields = ['project__title']
    readonly_fields = ['date']
    date_hierarchy = 'date'


@admin.register(CreatorPayout)
class CreatorPayoutAdmin(admin.ModelAdmin):
    list_display = ['creator', 'amount', 'status', 'payout_method', 'requested_at']
    list_filter = ['status', 'payout_method', 'requested_at']
    search_fields = ['creator__username', 'payout_email', 'transaction_id']
    readonly_fields = ['id', 'requested_at', 'processed_at', 'completed_at']
    actions = ['mark_processing', 'mark_completed', 'mark_failed']
    
    fieldsets = (
        ('Creator Info', {
            'fields': ('id', 'creator', 'amount')
        }),
        ('Payout Details', {
            'fields': ('payout_method', 'payout_email', 'transaction_id')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'processed_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mark_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} payouts marked as processing')
    mark_processing.short_description = "Mark as processing"
    
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} payouts marked as completed')
    mark_completed.short_description = "Mark as completed"
    
    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payouts marked as failed')
    mark_failed.short_description = "Mark as failed"


@admin.register(AITagSuggestion)
class AITagSuggestionAdmin(admin.ModelAdmin):
    list_display = ['project', 'suggested_tags', 'applied', 'created_at']
    list_filter = ['applied', 'created_at']
    search_fields = ['project__title']
    readonly_fields = ['created_at']
