from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, ModerationReport


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
