import logging

from flask import g

from src.repositories.partner_lab_repository import PartnerLabRepository

logger = logging.getLogger(__name__)


class AuthenticateLabQuery:

    def __init__(self, session_factory):
        self.repository = PartnerLabRepository(session_factory)

    def execute(self, lab_id, lab_token):
        logger.info(f'{g.trace_id} --- executing AuthenticateLabQuery for lab {lab_id}')
        return self.repository.query_lab_authenticity(lab_id, lab_token)
