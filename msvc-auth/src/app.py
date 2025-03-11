import logging
import sys
import threading
import time
import uuid

import jwt

from flask import Flask, request, jsonify, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL, DB_HOST, DB_PORT, DB_NAME
from src.models.partner_lab import Base
from src.queries.authenticate_lab_query import AuthenticateLabQuery

# Configure logging
gunicorn_logger = logging.getLogger('gunicorn.error')

# Configure logging to work with Gunicorn
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

# Create Flask app
app = Flask(__name__)

logger.info(f'Connecting to database at {DB_HOST}:{DB_PORT}/{DB_NAME}')
engine = create_engine(DATABASE_URL)
# Test connection
with engine.connect() as conn:
    conn.execute('SELECT 1')

logger.info('Database connection established')

session_factory = sessionmaker(bind=engine)
logger.info('Session object created')

Base.metadata.create_all(engine)
logger.info('checked/created all tables')


@app.route('/authenticate/partner-lab', methods=['GET'])
def authenticate_lab():
    if request.headers.get('Content-Type') != 'application/x-www-form-urlencoded':
        return jsonify({'error': 'Invalid Content-Type'}), 400

    logger.info(f'{g.trace_id} --- authenticating partner lab')

    lab_id = request.args.get('lab_id')
    lab_token = request.args.get('lab_token')

    logger.info(f'{g.trace_id} --- info got was: {lab_token}, {lab_id}')

    was_checked = AuthenticateLabQuery(session_factory).execute(lab_id, lab_token)
    if was_checked:
        logger.info(f'{g.trace_id} --- authentication was successful :: info got was: {lab_token}, {lab_id}')
        return jsonify({'message': 'Authentication successful'}, 200)
    else:
        logger.info(f'{g.trace_id} --- authentication failed :: info got was: {lab_token}, {lab_id}')
        return jsonify({'message': 'Authentication failed, unauthorized'}), 401


@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'msvc-auth is healthy'}, 200


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
