from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class KafkaHandler:
    def __init__(self):
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=os.getenv("KAFKA_BROKER_URL", "localhost:9092"),
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = os.getenv("KAFKA_TOPIC", "file-upload-events")

    def send_event(self, event_data):
        """
        Send an event message to the Kafka topic.
        :param event_data: dict containing event information.
        """
        try:
            self.producer.send(self.topic, value=event_data)
            self.producer.flush()
            print(f"Event sent to Kafka: {event_data}")
            return {"success": True}
        except Exception as e:
            print(f"Error sending event to Kafka: {str(e)}")
            return {"success": False, "error": str(e)}
