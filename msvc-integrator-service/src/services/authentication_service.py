import logging
import sys

import requests
from flask import g

from src.config import Config

URL_ENCODED_HEADER = {
    "Content-Type": "application/x-www-form-urlencoded"
}

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


class AuthenticationService:

    @staticmethod
    def authenticate_user(lab_id, lab_token):
        logger.info(f'{g.trace_id} --- sending: {lab_token}, {lab_id}')

        response = requests.get(f'{Config.AUTH_URL}/authenticate/partner-lab', params={
            'lab_id': lab_id,
            'lab_token': lab_token,
        }, headers=URL_ENCODED_HEADER)

        logger.info(f'{g.trace_id} --- got response from authentication service, code was %s', response.status_code)

        if response.status_code != 200:
            return None

        return response.json()
