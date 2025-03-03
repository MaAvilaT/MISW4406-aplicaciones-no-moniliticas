import json
import logging

import pika
from pika.exceptions import AMQPConnectionError

from src.commands.store_lab_test_command import StoreLabTestCommand
from src.config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASS,
    RABBITMQ_QUEUE
)

logger = logging.getLogger(__name__)


class LabTestConsumer:
    """Consumer for lab test messages from RabbitMQ"""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.command = StoreLabTestCommand(session_factory)
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection to RabbitMQ"""
        logger.info(f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")

        # Setup connection parameters
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        # Connect to RabbitMQ server
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Declare queue (This ensures the queue exists)
        self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        logger.info(f"Connected to RabbitMQ, consuming from queue: {RABBITMQ_QUEUE}")

    def process_message(self, ch, method, properties, body):
        """
        Process incoming message from RabbitMQ

        Args:
            ch: Channel
            method: Method
            properties: Properties
            body: Message body
        """
        try:
            # Parse message body
            logger.info(f"Received payload: {body}")
            message = json.loads(body)
            logger.info(f"Received message for patient: {message.get('patient_uuid', 'unknown')}")

            # Extract data from message
            lab_id = message.get('lab_id')
            lab_token = message.get('lab_token')
            lab_document = message.get('lab_document')
            patient_uuid = message.get('patient_uuid')

            # Validate required fields
            if not all([lab_id, lab_token, lab_document, patient_uuid]):
                logger.error(f"Message missing required fields: {message}")
                # Acknowledge the message even if it's invalid to avoid queue blocking
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Execute command to store lab test
            self.command.execute(lab_id, lab_token, lab_document, patient_uuid)

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Successfully processed message for patient: {patient_uuid}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {body}")
            # Acknowledge invalid messages to avoid queue blocking
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Reject the message and requeue it
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Start consuming messages from RabbitMQ"""
        try:
            self.connect()

            # Set QoS prefetch count
            self.channel.basic_qos(prefetch_count=1)

            # Start consuming
            self.channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=self.process_message
            )

            logger.info("Starting to consume messages...")
            self.channel.start_consuming()

        except AMQPConnectionError as e:
            logger.error(f"AMQP Connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in consumer: {str(e)}")
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            raise

    def stop(self):
        """Stop consuming messages and close connection"""
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()

        if self.connection and not self.connection.is_closed:
            self.connection.close()

        logger.info("Consumer stopped")