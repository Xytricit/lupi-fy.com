from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot_page'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/clear/', views.clear_chat, name='clear_chat'),
    path('api/history/', views.chat_history, name='chat_history'),
    path('api/analytics/', views.user_analytics, name='user_analytics'),
    path('api/insights/', views.dashboard_insights, name='dashboard_insights'),
]
