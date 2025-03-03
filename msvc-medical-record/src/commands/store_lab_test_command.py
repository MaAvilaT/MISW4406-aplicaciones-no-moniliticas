import logging
from src.repositories.lab_test_repository import LabTestRepository

logger = logging.getLogger(__name__)


class StoreLabTestCommand:
    """Command for storing a lab test result in the database"""

    def __init__(self, session_factory):
        self.repository = LabTestRepository(session_factory)

    def execute(self, lab_id, lab_token, lab_document, patient_uuid):
        """
        Execute the command to store a lab test result

        Args:
            lab_id: SHA256 hash identifying the lab
            lab_token: JWT or API Key for the lab
            lab_document: JSON object with lab test data
            patient_uuid: SHA256 hash identifying the patient

        Returns:
            The created lab test record
        """
        logger.info(f"Executing StoreLabTestCommand for patient {patient_uuid}")
        return self.repository.save(lab_id, lab_token, lab_document, patient_uuid)