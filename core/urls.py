from django.urls import path
from core import views as core_views
from blog.views import posts_list_view
from accounts import views as accounts_views
from communities import views as communities_views

urlpatterns = [
    path('', core_views.main_home_view, name='main_home'),
    path('dashboard/', core_views.dashboard_view, name='dashboard_home'),
    path('dashboard/community-posts-api/', core_views.community_posts_api, name='community_posts_api'),
    path('blogs/', posts_list_view, name='blogs'),

    # Use the correct communities view
    path('communities/', communities_views.communities_list, name='communities'),
    path('communities/toggle/<int:community_id>/', communities_views.toggle_join_community, name='toggle_join_community'),

    path('subscriptions/', accounts_views.subscriptions_view, name='subscriptions'),
    # path("subscribe/<int:community_id>/", core_views.toggle_subscription, name="toggle_subscription"),  # optional, remove or comment
]
