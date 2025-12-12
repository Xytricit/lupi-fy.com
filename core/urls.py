from django.urls import path

from accounts import views as accounts_views
from blog.views import posts_list_view
from communities import views as communities_views
from core import views as core_views

urlpatterns = [
    path("", core_views.main_home_view, name="main_home"),
    path("dashboard/", core_views.dashboard_view, name="dashboard_home"),
    path(
        "dashboard/community-posts-api/",
        core_views.community_posts_api,
        name="community_posts_api",
    ),
    path(
        "dashboard/search-suggestions/",
        core_views.search_suggestions,
        name="search_suggestions",
    ),
    path("search/", core_views.search_page, name="search_page"),
    path("search/api/", core_views.search_api, name="search_api"),
    path("blogs/", posts_list_view, name="blogs"),
    # Terms & Conditions
    path("terms-of-service", core_views.terms_of_service_view, name="terms_of_service"),
    # Use the correct communities view
    path("communities/", communities_views.communities_list, name="communities"),
    path(
        "communities/toggle/<int:community_id>/",
        communities_views.toggle_join_community,
        name="toggle_join_community",
    ),
    path("subscriptions/", accounts_views.subscriptions_view, name="subscriptions"),
    # path("subscribe/<int:community_id>/", core_views.toggle_subscription, name="toggle_subscription"),  # optional, remove or comment
]
