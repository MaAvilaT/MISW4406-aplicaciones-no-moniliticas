import json
from src.services.rabbitmq_service import RabbitMQService
import threading


class LabResultsBatchSubmittedEvent:

    _instance = None
    _lock = threading.Lock()  # Thread safety for Singleton initialization

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LabResultsBatchSubmittedEvent, cls).__new__(cls)
                    cls._instance.__init_once()  # Call custom init method
        return cls._instance

    def __init_once(self):
        self.rabbitmq_service = RabbitMQService()

    def publish_to_queue(self, queue_data):
        # Publish the message to RabbitMQ
        message_id = self.rabbitmq_service.publish_message(json.dumps(queue_data))

        return message_id
