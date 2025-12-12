from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from datetime import timedelta

from django.utils import timezone

from .models import (Conversation, CustomUser, DirectMessage, GameLobbyBan,
                     LetterSetGame, ModerationReport)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_verified",
        "is_premium",
        "warning_count",
        "suspended_until",
    )

    actions = [
        "deactivate_users",
        "activate_users",
        "ban_users_7_days",
        "ban_users_permanent",
        "lift_bans",
    ]

    fieldsets = UserAdmin.fieldsets + (
        (
            "User Info",
            {"fields": ("bio", "avatar", "color", "is_verified", "is_premium")},
        ),
        ("Moderation", {"fields": ("warning_count", "suspended_until")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)


def _set_users_active(queryset, active=True):
    queryset.update(is_active=active)


def deactivate_users(modeladmin, request, queryset):
    _set_users_active(queryset, False)
    modeladmin.message_user(request, f"Deactivated {queryset.count()} user(s)")


deactivate_users.short_description = "Deactivate selected users"


def activate_users(modeladmin, request, queryset):
    _set_users_active(queryset, True)
    modeladmin.message_user(request, f"Activated {queryset.count()} user(s)")


activate_users.short_description = "Activate selected users"


def ban_users_7_days(modeladmin, request, queryset):
    until = timezone.now() + timedelta(days=7)
    queryset.update(suspended_until=until)
    modeladmin.message_user(request, f"Banned {queryset.count()} user(s) for 7 days")


ban_users_7_days.short_description = "Ban selected users for 7 days"


def ban_users_permanent(modeladmin, request, queryset):
    # Set suspended_until far in the future (100 years)
    until = timezone.now() + timedelta(days=365 * 100)
    queryset.update(suspended_until=until)
    modeladmin.message_user(request, f"Permanently banned {queryset.count()} user(s)")


ban_users_permanent.short_description = "Permanently ban selected users"


def lift_bans(modeladmin, request, queryset):
    queryset.update(suspended_until=None)
    modeladmin.message_user(request, f"Lifted bans for {queryset.count()} user(s)")


lift_bans.short_description = "Lift bans for selected users"


@admin.register(ModerationReport)
class ModerationReportAdmin(admin.ModelAdmin):
    list_display = ("user", "timestamp", "resolved")
    list_filter = ("resolved", "timestamp")
    search_fields = ("user__username", "post_content", "banned_words_found")


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "recipient", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__username", "recipient__username", "content")
    readonly_fields = ("created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("user1", "user2", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user1__username", "user2__username")


@admin.register(GameLobbyBan)
class GameLobbyBanAdmin(admin.ModelAdmin):
    list_display = ("user", "banned_until", "created_at")
    list_filter = ("created_at", "banned_until")
    search_fields = ("user__username",)
    readonly_fields = ("created_at",)


@admin.register(LetterSetGame)
class LetterSetGameAdmin(admin.ModelAdmin):
    list_display = ("user", "letters", "score", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__username",)
    readonly_fields = ("created_at", "updated_at")
