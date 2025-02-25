import json
import logging
import os
import re

from flask import Flask, request, jsonify
import pika
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')

# Handle the case where RABBITMQ_PORT is a URL
rabbitmq_port_env = os.environ.get('RABBITMQ_PORT', '5672')
# Check if it's a URL and extract just the port number if needed
if '://' in rabbitmq_port_env:
    match = re.search(r':(\d+)$', rabbitmq_port_env)
    RABBITMQ_PORT = int(match.group(1)) if match else 5672
else:
    RABBITMQ_PORT = int(rabbitmq_port_env)

RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
QUEUE_NAME = os.environ.get('QUEUE_NAME', 'message_queue')


def get_rabbitmq_connection():
    retry_count = 0
    max_retries = 5

    while retry_count < max_retries:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600
            )
            connection = pika.BlockingConnection(parameters)
            logger.info("Successfully connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            retry_count += 1
            wait_time = 5 * retry_count
            logger.warning(f"Failed to connect to RabbitMQ, retrying in {wait_time}s... ({retry_count}/{max_retries})")
            time.sleep(wait_time)

    logger.error("Failed to connect to RabbitMQ after maximum retries")
    raise Exception("Could not connect to RabbitMQ")


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route('/send', methods=['POST'])
def send_message():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    message = request.get_json()

    try:
        # Establish connection to RabbitMQ
        connection = get_rabbitmq_connection()
        channel = connection.channel()

        # Declare queue
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )

        connection.close()
        logger.info(f"Message sent to queue: {QUEUE_NAME}")

        return jsonify({
            "status": "success",
            "message": "Message sent to queue",
            "queue": QUEUE_NAME
        }), 200

    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
