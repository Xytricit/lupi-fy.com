from django.urls import path

from . import views

urlpatterns = [
    path("onboarding/", views.onboarding_view, name="onboarding_view"),
    path("for-you/", views.for_you_recommendations, name="for_you_recommendations"),
    path("interests/", views.get_user_interests, name="get_user_interests"),
    path("interests/save/", views.save_user_interests, name="save_user_interests"),
    path(
        "blog-recommendations/",
        views.get_blog_recommendations,
        name="get_blog_recommendations",
    ),
    path(
        "community-recommendations/",
        views.get_community_recommendations,
        name="get_community_recommendations",
    ),
    path(
        "games-recommendations/",
        views.get_game_recommendations,
        name="get_game_recommendations",
    ),
    path(
        "marketplace-recommendations/",
        views.get_marketplace_recommendations,
        name="get_marketplace_recommendations",
    ),
    path(
        "hybrid-recommendations/",
        views.get_hybrid_recommendations,
        name="get_hybrid_recommendations",
    ),
    path("tag-options/", views.get_tag_options, name="get_tag_options"),
    path("track-interaction/", views.track_interaction, name="track_interaction"),
]
