import logging
import sys

from flask import g
from sqlalchemy.orm import Session
from sqlalchemy import and_
from src.models.partner_lab import PartnerLab

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


class PartnerLabRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def query_lab_authenticity(self, lab_id, lab_token):
        session: Session = self.session_factory()
        try:
            logger.info(f'{g.trace_id} --- partner_lab::{lab_id}, {lab_token}')

            partner_lab = session.query(PartnerLab).filter(
                and_(PartnerLab.lab_id == lab_id, PartnerLab.lab_token == lab_token)
            ).all()

            logger.info(f'{g.trace_id} --- got {len(partner_lab)} partner_labs')

            if len(partner_lab) != 1:
                return False

            return True
        except Exception as e:
            logger.error(f'{g.trace_id} --- error authenticating partner lab, it was: {str(e)}')
            session.close()
            raise
