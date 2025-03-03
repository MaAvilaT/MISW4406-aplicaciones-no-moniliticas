import json
from datetime import datetime


class LabResultSubmittedEvent:
    """
    Evento que se produce cuando se envía un resultado de laboratorio correctamente.
    Siguiendo el patrón CQS, este evento no modifica el estado, solo lo representa.
    """

    def __init__(self, lab_id, patient_uuid, message_id=None):
        self.lab_id = lab_id
        self.patient_uuid = patient_uuid
        self.message_id = message_id
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self):
        """Convierte el evento a un diccionario."""
        return {
            "event_type": "lab_result_submitted",
            "lab_id": self.lab_id,
            "patient_uuid": self.patient_uuid,
            "message_id": self.message_id,
            "timestamp": self.timestamp
        }

    def to_json(self):
        """Convierte el evento a JSON."""
        return json.dumps(self.to_dict())
