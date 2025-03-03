import pika
import json
import uuid
from src.config import Config
import logging

logger = logging.getLogger(__name__)


class RabbitMQService:
    """
    Servicio para interactuar con RabbitMQ.
    Proporciona métodos para publicar mensajes en colas.
    """

    def __init__(self):
        self.host = Config.RABBITMQ_HOST
        self.port = Config.RABBITMQ_PORT
        self.user = Config.RABBITMQ_USER
        self.password = Config.RABBITMQ_PASSWORD
        self.vhost = Config.RABBITMQ_VHOST
        self.queue_name = Config.LAB_RESULT_QUEUE
        self.connection = None
        self.channel = None
        self.create_connection()

    def create_connection(self):
        # prevents accidental connection creation over each single request
        if self.connection and self.connection.is_open:
            return self.connection

        """Establece y devuelve una conexión a RabbitMQ."""
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.vhost,
            credentials=credentials,
            connection_attempts=3,
            retry_delay=5,
            socket_timeout=Config.CONNECTION_TIMEOUT
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='my_queue', durable=True)

    def publish_message(self, message):
        """Publica un mensaje en la cola de RabbitMQ."""
        connection = None
        try:
            if self.connection.is_closed:
                self.create_connection()

            connection = self.connection
            channel = connection.channel()

            # Declarar la cola como duradera
            channel.queue_declare(queue=self.queue_name, durable=True)

            # Generar un ID único para el mensaje
            message_id = str(uuid.uuid4())

            # Publicar el mensaje
            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensaje persistente
                    message_id=message_id,
                    content_type='application/json',
                    headers={
                        'source': 'msvc-integrator-service',
                        'type': 'lab_result'
                    }
                )
            )

            logger.info(f"message published {self.queue_name} with ID: {message_id}")
            return message_id

        except Exception as e:
            logger.error(f"error when attempting to publish RabbitMQ message: {str(e)}")
            raise
