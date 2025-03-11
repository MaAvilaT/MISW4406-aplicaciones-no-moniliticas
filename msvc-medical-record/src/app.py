import logging
import sys
import threading
import time
import uuid

from flask import Flask, request, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL, DB_HOST, DB_PORT, DB_NAME
from src.consumers.lab_test_consumer import LabTestConsumer
from src.models.lab_test import Base

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

app = Flask(__name__)


def start_consumer():
    max_retries = 5
    retry_delay = 5  # seconds

    session_factory = None

    for attempt in range(max_retries):
        try:
            logger.info(f'Connecting to database at {DB_HOST}:{DB_PORT}/{DB_NAME}')
            engine = create_engine(DATABASE_URL)
            # Test connection
            with engine.connect() as conn:
                conn.execute('SELECT 1')

            logger.info(f'database connection established')

            session_factory = sessionmaker(bind=engine)
            logger.info(f'session object created')

            Base.metadata.create_all(engine)
            logger.info(f'checked all tables')

            break
        except Exception as e:
            logger.error(
                f'failed to connect to database (attempt {attempt + 1}/{max_retries}): {str(e)}')
            if attempt < max_retries - 1:
                logger.info(f'retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                logger.error(f'max retries reached. cannot connect to database.')
                exit(1)

    if not session_factory:
        raise Exception('Failed to connect to database.')

    logger.info(f'starting RabbitMQ consumer')
    consumer = LabTestConsumer(session_factory)

    max_retries = 5
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            consumer.start()
            break
        except Exception as e:
            logger.error(
                f'failed to connect to RabbitMQ (attempt {attempt + 1}/{max_retries}): {str(e)}')
            if attempt < max_retries - 1:
                logger.info(f'retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                logger.error(f'max retries reached. Exiting...')


consumer_thread = threading.Thread(target=start_consumer)
consumer_thread.daemon = True
consumer_thread.start()


@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200


@app.before_request
def assign_trace_id():
    trace_id = request.headers.get('X-Trace-Id', str(uuid.uuid4()))
    g.trace_id = trace_id
    logger.info(f'incoming request with trace-id: {trace_id}')


@app.after_request
def add_trace_id_header(response):
    response.headers['X-Trace-Id'] = g.trace_id
    return response


if __name__ == '__main__':
    # Start Flask application
    app.run(host='0.0.0.0', port=5000)
