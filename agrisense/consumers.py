import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

class SoilConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user or user.is_anonymous:
            await self.close(code=403)
            return

        self.user = user
        self.group_name = f"user_{user.id}_soil"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"✅ Soil WebSocket connected for {user.username}")

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"❌ Soil WebSocket disconnected for {getattr(self.user, 'username', 'unknown')}")

    # ✅ Receive messages from WebSocket (simulator)
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                message = json.loads(text_data)
                if message.get("type") == "soil_update":
                    # Forward to group so the frontend gets it
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "soil_update",
                            "data": message["data"]
                        }
                    )
            except Exception as e:
                print(f"⚠️ Error parsing message: {e}")

    # ✅ Receive messages from group and send to frontend
    async def soil_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "soil_update",
            "data": event["data"]
        })
        )

    


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.user = user
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"✅ WS Connected for {user.username}")

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"❌ WS Disconnected for {getattr(self.scope['user'], 'username', 'unknown')}")

    async def send_notification(self, event):
        """
        Event sent by Celery to WebSocket group.
        """
        message = event.get("message", {})

        # ✅ Send the message directly (no extra wrapping)
        await self.send(text_data=json.dumps(message))
        print(f"📩 Sent to {getattr(self.scope['user'], 'username', 'unknown')}: {message}")
