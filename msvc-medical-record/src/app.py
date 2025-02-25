# consumer/app.py
import json
import logging
import os
import threading
import re
import time
import pika
from flask import Flask, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RabbitMQ connection parameters
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_port_env = os.environ.get('RABBITMQ_PORT', '5672')

# Extract port number if it's a URL
if '://' in rabbitmq_port_env:
    match = re.search(r':(\d+)$', rabbitmq_port_env)
    RABBITMQ_PORT = int(match.group(1)) if match else 5672
else:
    RABBITMQ_PORT = int(rabbitmq_port_env)

RABBITMQ_USER = os.environ.get('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS', 'guest')
QUEUE_NAME = os.environ.get('QUEUE_NAME', 'message_queue')

# In-memory storage for received messages (for testing)
received_messages = []

def message_callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        logger.info(f'Received message: {message}')

        # Store the message
        received_messages.append({
            'message': message,
            'received_at': time.strftime('%Y-%m-%d %H:%M:%S')
        })

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except json.JSONDecodeError:
        logger.error(f'Error decoding message: {body}')
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge bad messages to avoid infinite requeue

    except Exception as e:
        logger.error(f'Error processing message: {str(e)}')
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Avoid infinite retries



# Establish connection
connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()

# Declare the queue (ensure it exists)
channel.queue_declare(queue=QUEUE_NAME, durable=True)


# Set up consumer
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=message_callback)

print(f'Waiting for messages on queue: {QUEUE_NAME}')
channel.start_consuming()


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200


@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({
        'message_count': len(received_messages),
        'messages': received_messages
    })


@app.route('/clear', methods=['POST'])
def clear_messages():
    received_messages.clear()
    return jsonify({'status': 'success', 'message': 'Message history cleared'})


if __name__ == '__main__':
    # Start Flask server
    app.run(host='0.0.0.0', port=5000)
