import json
import hashlib
import uuid
import jwt
from datetime import datetime, timedelta
from src.config import Config


class LabResultNormalizer:

    def __init__(self, lab_id, lab_token, lab_document: dict):
        self.lab_id = lab_id
        self.lab_token = lab_token
        self.lab_document = lab_document
        self.patient_uuid = self.lab_document['patient_uuid']

        if 'patient_name' in self.lab_document:
            del self.lab_document['patient_name']

    def to_dict(self):
        return {
            'lab_id': self.lab_id,
            'lab_token': self.lab_token,
            'lab_document': self.lab_document,
            'patient_uuid': self.patient_uuid,
            'timestamp': datetime.utcnow().isoformat()
        }
