# drivers/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
        else:
            self.driver = await self.get_driver(user)
            self.group_name = f"driver_{self.driver.id}"

            # Join group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

    @database_sync_to_async
    def get_driver(self, user):
        return user.driver

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude and longitude:
            # Update driver's location in the database
            await self.update_driver_location(latitude, longitude)

            # Optionally, broadcast the location to other interested parties
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'location_update',
                    'latitude': latitude,
                    'longitude': longitude,
                }
            )

    @database_sync_to_async
    def update_driver_location(self, latitude, longitude):
        self.driver.current_location = Point(float(longitude), float(latitude))
        self.driver.save()

    # Receive location update from group
    async def location_update(self, event):
        latitude = event['latitude']
        longitude = event['longitude']

        # Send location update to WebSocket
        await self.send(text_data=json.dumps({
            'latitude': latitude,
            'longitude': longitude,
        }))
