
# logistics_platform/kafka_consumer.py
from kafka import KafkaConsumer
import json
from django.core.cache import cache
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def consume_driver_location():
    consumer = KafkaConsumer(
        'location_topic',
        bootstrap_servers=['localhost:29092'],
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='driver-location-group'
    )

    channel_layer = get_channel_layer()
    for message in consumer:
        driver_data = message.value
        # print(driver_data)
        driver_id = driver_data['driver_id']
        latitude = driver_data['latitude']
        longitude = driver_data['longitude']
        
        # Store the location update in cache or database
        print(f"Received location update for driver {driver_id}: {latitude}, {longitude}")
        cache.set(f'driver_{driver_id}_location', (latitude, longitude), timeout=60)

        async_to_sync(channel_layer.group_send)(
            f'driver_{driver_id}_location',
            {
                'type': 'send_location_update',
                'driver_id': driver_id,
            }
        )
# To run the consumer:
if __name__ == '__main__':
    consume_driver_location()
# consume_driver_location()


# channel_layer = get_channel_layer()

# def process_location_updates():
#     for message in consumer:
#         data = message.value
#         driver_id = data['driver_id']
#         latitude = data['latitude']
#         longitude = data['longitude']

#         # Update driver location
#         driver = Driver.objects.get(id=driver_id)
#         driver.current_location = Point(longitude, latitude)
#         driver.save()

#         # Find nearby pending bookings
#         nearby_bookings = Booking.objects.filter(
#             status='PENDING',
#             pickup_location__distance_lte=(driver.current_location, D(km=5))
#         )

#         # Send notifications to nearby drivers
#         for booking in nearby_bookings:
#             async_to_sync(channel_layer.group_send)(
#                 f'driver_{driver.id}',
#                 {
#                     'type': 'booking_notification',
#                     'booking_id': booking.id,
#                     'pickup_address': booking.pickup_address
#                 }
#             )

# if __name__ == '__main__':
#     process_location_updates()


"""
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "coordinates": [
          [
            78.34791094571796,
            17.494464613199213
          ],
          [
            78.34743118157394,
            17.494575539984822
          ],
          [
            78.34658795974605,
            17.494769661697546
          ],
          [
            78.34589012099241,
            17.494852856654248
          ],
          [
            78.3455702782287,
            17.494922185755485
          ],
          [
            78.3452213588526,
            17.494936051572125
          ],
          [
            78.34484336285959,
            17.494936051572125
          ],
          [
            78.34445082856035,
            17.49499151482958
          ],
          [
            78.34408737087654,
            17.495005380641615
          ],
          [
            78.34366575996182,
            17.49504697807083
          ],
          [
            78.34324414904717,
            17.4950747096847
          ],
          [
            78.34285161474799,
            17.49510244129442
          ],
          [
            78.34289522966958,
            17.494603271671394
          ],
          [
            78.34286615305564,
            17.494145698312323
          ],
          [
            78.34286615305564,
            17.493577196474334
          ],
          [
            78.34280799982639,
            17.493286011917405
          ]
        ],
        "type": "LineString"
      }
    }
  ]
}
"""