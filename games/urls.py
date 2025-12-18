from django.urls import path
from . import views
from . import views_advanced

urlpatterns = [
    # Games Hub
    path('', views.games_hub_view, name='games_hub'),
    path('block-burst/', views.block_burst_view, name='block_burst'),
    
    path('api/recently-played/', views.recently_played_api, name='recently_played_api'),
    path('editor/', views.editor_view, name='editor'),
    path('editor-debug/', views.editor_debug_view, name='editor_debug'),
    path('editor-enhanced/', views.editor_view, {'version': 'enhanced'}, name='editor_enhanced'),
    path('editor-guest/', views.editor_public_view, name='editor_guest'),
    # Dashboard for game editor: lists user's games, drafts, analytics
    path('dashboard/', views.editor_dashboard_view, name='dashboard'),
    path('dashboard/home/', views.dashboard_home_view, name='games_dashboard_home'),
    path('multiplayer/', views.multiplayer_view, name='multiplayer'),
    path('tutorial/', views.tutorial_view, name='tutorial'),
    path('moderation/', views.moderation_view, name='moderation'),
    path('api/save/', views.save_game_api, name='save_game'),
    path('api/publish/', views.publish_game_api, name='publish_game'),
    path('api/approve/', views.approve_game_api, name='approve_game'),
    path('api/reject/', views.reject_game_api, name='reject_game'),
    path('api/games-list/', views.games_list_api, name='games_list'),
    path('api/upload-asset/', views.upload_asset_api, name='upload_asset'),
    path('api/list-assets/', views.list_assets_api, name='list_assets'),
    path('api/submit-score/', views.submit_score_api, name='submit_score'),
    path('api/leaderboard/', views.leaderboard_api, name='leaderboard'),
    path('api/achievements/', views.user_achievements_api, name='user_achievements'),
    path('api/analyze-logic/', views.analyze_logic_api, name='analyze_logic'),
    path('api/creator-revenue/', views.creator_revenue_api, name='creator_revenue'),
    
    # Advanced Features
    # Multiplayer
    path('api/multiplayer/create-session/', views_advanced.create_multiplayer_session, name='create_session'),
    path('api/multiplayer/join-session/', views_advanced.join_multiplayer_session, name='join_session'),
    path('api/multiplayer/active-sessions/', views_advanced.list_active_sessions, name='active_sessions'),
    
    # AI Assistant
    path('api/ai/suggest-improvements/', views_advanced.ai_suggest_improvements, name='ai_suggestions'),
    path('api/ai/generate-starter/', views_advanced.ai_generate_starter_code, name='ai_starter'),
    
    # Moderation
    path('api/moderation/report-game/', views_advanced.report_game, name='report_game'),
    path('api/moderation/queue/', views_advanced.get_moderation_queue, name='mod_queue'),
    path('api/moderation/add-tag/', views_advanced.add_game_tag, name='add_tag'),
    
    # Creator Analytics
    path('api/creator/game-stats/', views_advanced.creator_game_stats, name='game_stats'),
    path('api/creator/dashboard/', views_advanced.creator_dashboard_data, name='dashboard'),

    # User games API: list/delete/share
    path('api/user/games/', views_advanced.user_games_api, name='user_games_api'),
    path('api/create/', views_advanced.create_game_api, name='create_game'),
    path('api/delete/', views_advanced.delete_game_api, name='delete_game'),
    path('api/share/', views_advanced.share_game_api, name='share_game'),
    
    # Notifications
    path('api/notifications/', views_advanced.get_notifications, name='get_notifications'),
    path('api/notifications/mark-read/', views_advanced.mark_notification_read, name='mark_read'),
    
    # User Profile & Social
    path('api/user/<str:username>/', views_advanced.get_user_profile, name='user_profile'),
    path('api/user/follow/', views_advanced.follow_user, name='follow_user'),
    path('api/user/profile-update/', views_advanced.update_user_profile, name='profile_update'),
    
    # Game Remixing
    path('api/remix/', views_advanced.remix_game, name='remix_game'),
]

