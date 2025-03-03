import json
import hashlib
import uuid
import jwt
from datetime import datetime, timedelta
from src.config import Config


class ProcessLabResultCommand:
    """
    Comando para procesar un resultado de laboratorio.
    Siguiendo el patrón CQS, este comando modifica el estado (envía a RabbitMQ).
    """

    def __init__(self, patient_id=None, lab_name=None, raw_data=None):
        self.patient_id = patient_id or str(uuid.uuid4())
        self.lab_name = lab_name or f"Lab-{uuid.uuid4()}"
        self.raw_data = raw_data or {}

    def generate_sha256(self, text):
        """Genera un hash SHA256 del texto proporcionado."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def generate_jwt_token(self, lab_id):
        """Genera un token JWT para el laboratorio."""
        payload = {
            'lab_id': lab_id,
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'iss': 'msvc-integrator-service'
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

    def generate_fake_lab_data(self):
        """Genera datos falsos de laboratorio si no se proporcionaron datos reales."""
        test_types = ['BLOOD', 'URINE', 'COVID19', 'CHOLESTEROL', 'GLUCOSE']
        results = ['NORMAL', 'ABNORMAL', 'POSITIVE', 'NEGATIVE', 'INCONCLUSIVE']

        # Usar datos proporcionados o generar datos falsos
        custom_data = self.raw_data.get('lab_document', {})

        default_data = {
            "test_id": str(uuid.uuid4()),
            "test_type": test_types[uuid.uuid4().int % len(test_types)],
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "result": results[uuid.uuid4().int % len(results)],
            "reference_range": "Normal range: 70-99 mg/dL",
            "doctor_id": self.generate_sha256(f"doctor-{uuid.uuid4()}"),
            "lab_notes": "Patient was fasting for 12 hours before the test."
        }

        # Combinar datos por defecto con datos personalizados
        return {**default_data, **custom_data}

    def to_dict(self):
        """Convierte el comando a un diccionario para ser enviado a RabbitMQ."""
        lab_id = self.generate_sha256(self.lab_name)
        lab_token = self.generate_jwt_token(lab_id)
        lab_document = self.generate_fake_lab_data()
        patient_uuid = self.generate_sha256(self.patient_id)

        return {
            "lab_id": lab_id,
            "lab_token": lab_token,
            "lab_document": lab_document,
            "patient_uuid": patient_uuid,
            "timestamp": datetime.utcnow().isoformat()
        }