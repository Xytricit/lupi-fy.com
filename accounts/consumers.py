import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import GameLobbyMessage


class GameLobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "game_lobby"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Send recent history (last 50 messages)
        messages = await sync_to_async(list)(
            GameLobbyMessage.objects.order_by("-created_at")[:50].values(
                "author_name", "content", "created_at", "is_system"
            )
        )
        # messages are reversed to chronological order
        for msg in reversed(messages):
            payload = {
                "author": (
                    msg.get("author_name") or "System"
                    if msg.get("is_system")
                    else msg.get("author_name") or "Unknown"
                ),
                "content": msg.get("content"),
                "created_at": (
                    msg.get("created_at").isoformat() if msg.get("created_at") else None
                ),
                "is_system": msg.get("is_system"),
            }
            await self.send(
                text_data=json.dumps({"type": "lobby.message", "message": payload})
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Handler invoked by group_send
    async def lobby_message(self, event):
        message = event.get("message")
        await self.send(
            text_data=json.dumps({"type": "lobby.message", "message": message})
        )


class DMConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer to receive direct message notifications for a user.

    Clients should connect to: /ws/dm/<user_id>/ and must be authenticated.
    The server will send events of type 'dm.message' with payload under 'message'.
    """

    async def connect(self):
        # Accept only if the connecting user matches the URL user_id
        self.user_id = self.scope["url_route"]["kwargs"].get("user_id")
        self.group_name = f"user_{self.user_id}"

        # verify authenticated user matches requested id
        if not self.scope.get("user") or not self.scope["user"].is_authenticated:
            await self.close()
            return

        if str(self.scope["user"].id) != str(self.user_id):
            # Do not allow subscribing to other users' channel
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # This consumer is read-only from client side; ignore incoming messages
        return

    async def dm_message(self, event):
        # Forward DM events to the client
        message = event.get("message")
        await self.send(
            text_data=json.dumps({"type": "dm.message", "message": message})
        )

    async def user_block(self, event):
        """Forward user block/unblock events to connected clients."""
        payload = event.get("payload")
        await self.send(
            text_data=json.dumps({"type": "user.block", "payload": payload})
        )
