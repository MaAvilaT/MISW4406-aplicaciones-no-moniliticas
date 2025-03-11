import logging
import sys
import traceback
from datetime import datetime

from flask import request, jsonify, current_app, g
from src.events.lab_result_submitted_event import LabResultsBatchSubmittedEvent
from src.handlers.lab_result_normalizer import LabResultNormalizer

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


class LabResultBatchPreprocessor:

    @staticmethod
    def preprocess_batch(lab_id, lab_token, data):
        try:
            if 'documents_batch' not in data:
                raise Exception('No documents batch was passed')

            logger.info(f'{g.trace_id} --- preprocessing Lab Result Batch, data is equal to {data}')

            documents_batch: list[dict] = data['documents_batch']

            queue_data: list[dict] = []

            for document in documents_batch:
                logger.info(f'{g.trace_id} --- document in batch was {document}')

                normalized_document = LabResultNormalizer(lab_id=lab_id, lab_token=lab_token, lab_document=document)
                queue_data.append(normalized_document.to_dict())

            message_data = {
                'lab_test_documents': queue_data,
                'current_timestamp': datetime.utcnow().isoformat(),
                'trace_id': g.trace_id,
            }

            message_id = LabResultsBatchSubmittedEvent().publish_to_queue(message_data)

            return jsonify({
                'status': 'success',
                'message': 'lab results batch sent to processing queue',
                'details': f'message_id::{message_id}'
            }), 202

        except Exception as e:
            current_app.logger.error(f'{g.trace_id} --- error: {str(e)}')
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
