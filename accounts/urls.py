from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    # Google OAuth login page (replaces old register/login)
    path("login/", views.google_login_view, name="login"),
    # Traditional local login (fallback when OAuth missing)
    path("login/local/", views.login_view, name="local_login"),
    # Registration page (handles both Google OAuth and local signup)
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),
    path("subscriptions/", views.subscriptions_view, name="subscriptions"),
    path("account/", views.account_dashboard_view, name="account_dashboard"),
    # Email verification (deprecated - kept for backward compatibility)
    # path('verify-email/<int:user_id>/', views.verify_email, name='verify_email'),
    # path('resend-verification-email/<int:user_id>/', views.resend_verification_email, name='resend_verification_email'),
    # Real-time validation (deprecated - no longer needed with OAuth)
    # path('check-username/', views.check_username_available, name='check_username'),
    # path('check-email/', views.check_email_available, name='check_email'),
    # community subscription
    path(
        "toggle-subscription/<int:community_id>/",
        views.toggle_subscription,
        name="toggle_subscription",
    ),
    # author subscription
    path(
        "toggle-subscription/author/<int:author_id>/",
        views.toggle_subscription,
        name="toggle_subscription_author",
    ),
    # user profile popup
    path(
        "user/<int:user_id>/profile/", views.user_profile_view, name="user_profile_view"
    ),
    # public profile page
    path(
        "user/<int:user_id>/public-profile/",
        views.public_profile_view,
        name="public_profile_view",
    ),
    # Chat views
    path("chat/", views.chat_page_view, name="chat_page"),
    path("chat/<int:user_id>/", views.chat_page_view, name="chat_with_user"),
    path("api/send-message/", views.send_message_view, name="send_message"),
    path("api/get-messages/", views.get_messages_view, name="get_messages"),
    path(
        "api/get-conversations/", views.get_conversations_view, name="get_conversations"
    ),
    path("api/block-user/", views.block_user_api, name="block_user_api"),
    # Notifications
    path("notifications/", views.notifications_page_view, name="notifications_page"),
    path(
        "api/notifications/", views.get_notifications_api, name="get_notifications_api"
    ),
    path(
        "api/notifications/<int:notif_id>/mark-read/",
        views.mark_notification_read_api,
        name="mark_notification_read",
    ),
    # Game lobby
    path("game/lobby/", views.game_lobby_view, name="game_lobby"),
    path(
        "api/game/post-message/",
        views.game_lobby_post_message_view,
        name="game_post_message",
    ),
    # Games hub
    path("games/", views.games_hub_view, name="games_hub"),
    # Letter Set game
    path("games/letter-set/", views.letter_set_game_view, name="letter_set_game"),
    path(
        "api/game/letter-set/submit-word/",
        views.letter_set_submit_word_view,
        name="letter_set_submit_word",
    ),
    path(
        "api/game/letter-set/chat/", views.letter_set_chat_view, name="letter_set_chat"
    ),
    path(
        "api/game/letter-set/start/",
        views.letter_set_start_view,
        name="letter_set_start",
    ),
    # Lobby 12-word challenge
    path(
        "api/game/challenge/start/",
        views.game_lobby_challenge_start_view,
        name="game_challenge_start",
    ),
    # Creator / analytics
    path("creators/", views.creator_dashboard_view, name="creator_dashboard"),
    path(
        "api/post-analytics/<int:post_id>/",
        views.post_analytics_api,
        name="post_analytics_api",
    ),
    path("api/creator-chat/", views.creator_chat_api, name="creator_chat_api"),
    path("appearance/", views.appearance_view, name="appearance"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
