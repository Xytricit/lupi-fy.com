import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import GameLobbyMessage


class GameLobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'game_lobby'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send recent history (last 50 messages)
        messages = await sync_to_async(list)(
            GameLobbyMessage.objects.order_by('-created_at')[:50].values(
                'author_name', 'content', 'created_at', 'is_system'
            )
        )
        # messages are reversed to chronological order
        for msg in reversed(messages):
            payload = {
                'author': msg.get('author_name') or 'System' if msg.get('is_system') else msg.get('author_name') or 'Unknown',
                'content': msg.get('content'),
                'created_at': msg.get('created_at').isoformat() if msg.get('created_at') else None,
                'is_system': msg.get('is_system')
            }
            await self.send(text_data=json.dumps({'type': 'lobby.message', 'message': payload}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Handler invoked by group_send
    async def lobby_message(self, event):
        message = event.get('message')
        await self.send(text_data=json.dumps({'type': 'lobby.message', 'message': message}))
