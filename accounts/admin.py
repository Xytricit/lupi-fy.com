from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ModerationReport, DirectMessage, Conversation, GameLobbyBan, LetterSetGame


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 'email', 'is_staff',
        'is_verified', 'is_premium',
        'warning_count', 'suspended_until'
    )

    fieldsets = UserAdmin.fieldsets + (
        ("User Info", {
            'fields': ('bio', 'avatar', 'color', 'is_verified', 'is_premium')
        }),
        ("Moderation", {
            'fields': ('warning_count', 'suspended_until')
        }),
    )


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(ModerationReport)
class ModerationReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'resolved')
    list_filter = ('resolved', 'timestamp')
    search_fields = ('user__username', 'post_content', 'banned_words_found')


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'content')
    readonly_fields = ('created_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user1__username', 'user2__username')


@admin.register(GameLobbyBan)
class GameLobbyBanAdmin(admin.ModelAdmin):
    list_display = ('user', 'banned_until', 'created_at')
    list_filter = ('created_at', 'banned_until')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


@admin.register(LetterSetGame)
class LetterSetGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'letters', 'score', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


