import logging
import uuid
from sqlalchemy.orm import Session
from src.models.lab_test import LabTest

logger = logging.getLogger(__name__)


class LabTestRepository:

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def save(self, lab_id, lab_token, lab_document, patient_uuid):
        try:
            session: Session = self.session_factory()

            logger.info(f'type of the session factory object: {type(self.session_factory)}')
            logger.info(f'type of the session object: {type(session)}')

            lab_test = LabTest(
                id=str(uuid.uuid4()),
                lab_id=lab_id,
                lab_token=lab_token,
                lab_document=lab_document,
                patient_uuid=patient_uuid
            )

            logger.info(f'lab_test has the following data: {lab_test}')

            session.add(lab_test)
            session.commit()
            session.close()

            logger.info(f"Saved lab test result for patient {patient_uuid}")

            return lab_test

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving lab test: {str(e)}")
            session.close()
            raise
