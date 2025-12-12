from datetime import timedelta

from django.contrib import admin
from django.utils import timezone

from .models import ModerationReport, Post


@admin.register(ModerationReport)
class ModerationReportAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "timestamp", "resolved")
    list_filter = ("resolved", "timestamp")
    search_fields = ("user__username", "post__title", "post_content")
    readonly_fields = ("post_content", "banned_words_found", "timestamp")


def delete_posts(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f"Deleted {count} post(s)")


delete_posts.short_description = "Delete selected posts"


def ban_post_authors_7_days(modeladmin, request, queryset):
    authors = {p.author for p in queryset}
    until = timezone.now() + timedelta(days=7)
    for a in authors:
        a.suspended_until = until
        a.save()
    modeladmin.message_user(request, f"Banned {len(authors)} author(s) for 7 days")


ban_post_authors_7_days.short_description = "Ban authors of selected posts for 7 days"


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created", "updated")
    list_filter = ("created", "updated", "category")
    search_fields = ("title", "content", "author__username")
    actions = (delete_posts, ban_post_authors_7_days)
