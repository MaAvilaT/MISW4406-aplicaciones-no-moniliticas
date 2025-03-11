import logging
import sys
import uuid

from flask import Flask, jsonify, request, g
from prometheus_flask_exporter import PrometheusMetrics

from src.handlers.lab_result_batch_preprocessor import LabResultBatchPreprocessor
from src.services.authentication_service import AuthenticationService

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

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route('/api/lab-results', methods=['POST'])
@metrics.counter('lab_results_received', 'Number of lab results received')
def process_lab_results():
    logger.info(f'{g.trace_id} --- received lab results')

    if not request.json:
        return jsonify({'error': 'Request must be JSON'}), 400

    logger.info(f'{g.trace_id} --- validating lab_results request credentials')

    lab_id = request.headers.get('lab_id')
    lab_token = request.headers.get('lab_token')

    if not AuthenticationService.authenticate_user(lab_id, lab_token):
        return jsonify({'error': 'Authentication must be provided'}), 401

    logger.info(f'{g.trace_id} --- now preprocessing lab results')

    return LabResultBatchPreprocessor.preprocess_batch(lab_id, lab_token, request.json)


@app.route('/health/live', methods=['GET'])
def liveness():
    logger.info(f'{g.trace_id} --- liveness check')
    return jsonify({'status': 'ok', 'service': 'msvc-integrator-service'}), 200


@app.route('/health/ready', methods=['GET'])
def readiness():
    try:
        logger.info(f'{g.trace_id} --- readiness check')
        return jsonify({'status': 'ok', 'service': 'msvc-integrator-service'}), 200
    except Exception as e:
        app.logger.error(f'Readiness check failed: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 503


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
    app.run(host='0.0.0.0', port=5000)
