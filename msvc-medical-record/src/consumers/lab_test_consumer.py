import json
import logging
import sys

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

gunicorn_logger = logging.getLogger('gunicorn.error')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Send logs to stdout
    ]
)

logger = logging.getLogger(__name__)
logger.handlers = gunicorn_logger.handlers if gunicorn_logger.handlers else logger.handlers
logger.setLevel(gunicorn_logger.level if gunicorn_logger.level else logging.INFO)



class LabTestConsumer:

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.command = StoreLabTestCommand(session_factory)
        self.connection = None
        self.channel = None

    def connect(self):
        logger.info(f'connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}')

        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        logger.info(f'connected to RabbitMQ, consuming from queue: {RABBITMQ_QUEUE}')

    def process_message(self, ch, method, properties, body):
        decoded_str = body.decode("utf-8")

        message = json.loads(decoded_str)
        if isinstance(message, str):
            message = json.loads(message)

        logger.info(f'typeof message: {type(message)}')
        logger.info(f'received message: {message}')

        trace_id = message['trace_id']

        try:
            documents: dict = message['lab_test_documents']

            for document in documents:
                lab_id = document['lab_id']
                lab_token = document['lab_token']
                patient_uuid = document['patient_uuid']

                if not all([lab_id, lab_token, document, patient_uuid]):
                    logger.error(f'{trace_id} --- message missing required fields: {message}')
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                logger.error(f'{trace_id} --- executing save for lab test document: {document}')

                self.command.execute(lab_id, lab_token, document, patient_uuid)

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f'{trace_id} --- successfully processed message sent at {message["current_timestamp"]}')

        except json.JSONDecodeError:
            logger.error(f'{trace_id} --- invalid JSON message: {body}')
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f'{trace_id} --- error processing message: {str(e)}')
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        try:
            self.connect()

            self.channel.basic_qos(prefetch_count=1)

            self.channel.basic_consume(
                queue=RABBITMQ_QUEUE,
                on_message_callback=self.process_message
            )

            logger.info(f'starting to consume messages...')
            self.channel.start_consuming()

        except AMQPConnectionError as e:
            logger.error(f'AMQP Connection error: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'error in consumer: {str(e)}')
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            raise

    def stop(self):
        if self.channel and self.channel.is_open:
            self.channel.stop_consuming()

        if self.connection and not self.connection.is_closed:
            self.connection.close()

        logger.info(f'consumer stopped')
