import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notifications_{self.user_id}'

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
    async def send_notification(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class DriverBookingConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.driver_id = self.scope['url_route']['kwargs']['driver_id']
        self.group_name = f'driver_{self.driver_id}'

        # Join driver group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave driver group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive booking notifications
    async def booking_notification(self, event):
        await self.send_json({
            'type': 'booking_notification',
            'booking_id': event['booking_id'],
            'pickup_address': event['pickup_address'],
            'dropoff_address': event['dropoff_address'],
            'price': str(event['price']),
        })

    # Receive booking cancellation
    async def booking_cancelled(self, event):
        await self.send_json({
            'type': 'booking_cancelled',
            'booking_id': event['booking_id'],
        })
