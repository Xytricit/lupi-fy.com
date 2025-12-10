from django.urls import path
from accounts import consumers

websocket_urlpatterns = [
    path('ws/game/lobby/', consumers.GameLobbyConsumer.as_asgi()),
]
