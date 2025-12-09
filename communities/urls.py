from django.urls import path
from . import views

urlpatterns = [
    path('', views.communities_list, name='communities_list'),
    path('create/', views.create_community, name='create_community'),
    path('<int:community_id>/', views.community_detail, name='community_detail'),
    path('toggle/<int:community_id>/', views.toggle_join_community, name='toggle_join_community'),
    path('<int:community_id>/save/', views.save_community, name='save_community'),
    path('create-post/', views.create_community_post_generic, name='create_community_post_generic'),
    path('<int:community_id>/create-post/', views.create_community_post, name='create_community_post'),
    path('post/<int:post_id>/', views.community_post_detail, name='community_post_detail'),
]
