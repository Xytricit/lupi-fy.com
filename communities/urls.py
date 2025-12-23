from django.urls import path

from . import views

urlpatterns = [
    path("", views.communities_list, name="communities_list"),
    path("create/", views.create_community, name="create_community"),
    path("<int:community_id>/", views.community_detail, name="community_detail"),
    path("<int:community_id>/join/", views.join_community_ajax, name="join_community"),
    path("<int:community_id>/leave/", views.leave_community_ajax, name="leave_community"),
    path(
        "toggle/<int:community_id>/",
        views.toggle_join_community,
        name="toggle_join_community",
    ),
    path("<int:community_id>/save/", views.save_community, name="save_community"),
    path(
        "create-post/",
        views.create_community_post_generic,
        name="create_community_post_generic",
    ),
    path(
        "<int:community_id>/create-post/",
        views.create_community_post,
        name="create_community_post",
    ),
    path(
        "post/<int:post_id>/", views.community_post_detail, name="community_post_detail"
    ),
    path(
        "api/post/<int:post_id>/like/",
        views.toggle_community_post_like,
        name="toggle_community_post_like",
    ),
    path(
        "api/post/<int:post_id>/dislike/",
        views.toggle_community_post_dislike,
        name="toggle_community_post_dislike",
    ),
    path(
        "api/post/<int:post_id>/bookmark/",
        views.toggle_community_post_bookmark,
        name="toggle_community_post_bookmark",
    ),
    path(
        "api/post/<int:post_id>/comment/",
        views.add_community_post_comment,
        name="add_community_post_comment",
    ),
    path(
        "api/post/<int:post_id>/report/",
        views.report_community_post,
        name="report_community_post",
    ),
    path(
        "api/comment/<int:comment_id>/like/",
        views.toggle_community_comment_like,
        name="toggle_community_comment_like",
    ),
    path(
        "api/comment/<int:comment_id>/dislike/",
        views.toggle_community_comment_dislike,
        name="toggle_community_comment_dislike",
    ),
]
