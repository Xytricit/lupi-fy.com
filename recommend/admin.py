from django.contrib import admin

from .models import Interaction, Recommendation, UserInterests


@admin.register(UserInterests)
class UserInterestsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "game_categories",
        "blog_tags",
        "community_tags",
        "updated_at",
    )
    list_filter = (
        "completed_game_onboarding",
        "completed_blog_onboarding",
        "completed_community_onboarding",
    )
    search_fields = ("user__username",)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "content_type",
        "object_id",
        "value",
        "created_at",
    )
    list_filter = ("action", "content_type")
    search_fields = ("user__username",)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("user", "content_type", "object_id", "score", "created_at")
    list_filter = ("content_type",)
    search_fields = ("user__username",)
