from django.urls import path

from . import views

urlpatterns = [
    # --- Posts ---
    path("", views.posts_list_view, name="blogs"),
    path("create/", views.create_post_view, name="create_post"),
    path("moderation/", views.moderation_dashboard, name="moderation_dashboard"),
    path(
        "moderation/resolve/<int:report_id>/",
        views.resolve_report,
        name="resolve_report",
    ),
    path("blog/<int:pk>/", views.post_detail_view, name="post_detail"),
    # --- Blog API (for dynamic filtering/sorting) ---
    path("api/posts/", views.blog_posts_api, name="blog_posts_api"),
    # --- Post Actions ---
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("post/<int:post_id>/dislike/", views.toggle_dislike, name="toggle_dislike"),
    path("post/<int:post_id>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("post/<int:post_id>/report/", views.report_post, name="report_post"),
    # --- Comments ---
    path("post/<int:post_id>/comment/", views.post_comment, name="post_comment"),
    path("comment/<int:comment_id>/like/", views.like_comment, name="like_comment"),
    path("comment/<int:comment_id>/dislike/", views.dislike_comment, name="dislike_comment"),
    # --- Follow ---
    path("users/<int:author_id>/follow/", views.follow_user, name="follow_user"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
]
