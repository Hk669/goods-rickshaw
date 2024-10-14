# users/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class UserNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def booking_status_update(self, event):
        booking_id = event['booking_id']
        status = event['status']

        await self.send(text_data=json.dumps({
            'type': 'booking_status_update',
            'booking_id': booking_id,
            'status': status,
        }))

    async def tracking_update(self, event):
        booking_id = event['booking_id']
        data = event['data']

        await self.send(text_data=json.dumps({
            'type': 'tracking_update',
            'booking_id': booking_id,
            'data': data,
        }))
