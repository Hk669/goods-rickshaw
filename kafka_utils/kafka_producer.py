from kafka import KafkaProducer
import json
import time
import logging

logging.basicConfig(level=logging.INFO)

def run_kafka_producer():
    producer = KafkaProducer(
        bootstrap_servers='localhost:29092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "coordinates": [
                        [78.34791094571796, 17.494464613199213],
                        [78.34743118157394, 17.494575539984822],
                        [78.34658795974605, 17.494769661697546],
                        [78.34589012099241, 17.494852856654248],
                        [78.3455702782287, 17.494922185755485],
                        [78.3452213588526, 17.494936051572125],
                        [78.34484336285959, 17.494936051572125],
                        [78.34445082856035, 17.49499151482958],
                        [78.34408737087654, 17.495005380641615],
                        [78.34366575996182, 17.49504697807083],
                        [78.34324414904717, 17.4950747096847],
                        [78.34285161474799, 17.49510244129442],
                        [78.34289522966958, 17.494603271671394],
                        [78.34286615305564, 17.494145698312323],
                        [78.34286615305564, 17.493577196474334],
                        [78.34280799982639, 17.493286011917405]
                    ],
                    "type": "LineString"
                }
            }
        ]
    }

    while True:
        for coordinate in geojson_data['features'][0]['geometry']['coordinates']:
            driver_id = 6
            latitude = coordinate[1]
            longitude = coordinate[0]
            driver_data = {
                "driver_id": driver_id,
                "latitude": latitude,
                "longitude": longitude
            }
            future = producer.send('location_topic', driver_data)
            time.sleep(3)
            logging.info(f"Sent location data to Kafka: {driver_data}")
            # try:
            #     record_metadata = future.get(timeout=10)
            #     logging.info(f"Sent location data to Kafka: topic={record_metadata.topic}, partition={record_metadata.partition}, offset={record_metadata.offset}")
            # except Exception as e:
            #     logging.error(f"Failed to send location data to Kafka: {e}")
            #     time.sleep(3)  # Wait for 1-2 seconds (can be adjusted)


if __name__ == "__main__":
    run_kafka_producer()
