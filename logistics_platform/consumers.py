import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BookingStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.group_name = f"booking_status_{self.booking_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from group
    async def booking_status_update(self, event):
        status = event['status']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'status': status
        }))

class BookingTrackingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.booking_id = self.scope['url_route']['kwargs']['booking_id']
        self.group_name = f"booking_tracking_{self.booking_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive tracking update from group
    async def tracking_update(self, event):
        data = event['data']

        # Send data to WebSocket
        await self.send(text_data=json.dumps(data))
