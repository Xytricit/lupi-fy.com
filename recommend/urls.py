from django.urls import path

from . import views

urlpatterns = [
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
        "hybrid-recommendations/",
        views.get_hybrid_recommendations,
        name="get_hybrid_recommendations",
    ),
    path("tag-options/", views.get_tag_options, name="get_tag_options"),
]
