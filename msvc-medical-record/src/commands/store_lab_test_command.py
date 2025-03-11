import logging

from src.repositories.lab_test_repository import LabTestRepository

logger = logging.getLogger(__name__)


class StoreLabTestCommand:

    def __init__(self, session_factory):
        self.repository = LabTestRepository(session_factory)

    def execute(self, lab_id, lab_token, lab_document, patient_uuid):
        logger.info(f'Executing StoreLabTestCommand for patient {patient_uuid}')
        return self.repository.save(lab_id, lab_token, lab_document, patient_uuid)
