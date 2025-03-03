from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class LabTest(Base):
    """Model representing a laboratory test result in the database"""
    __tablename__ = 'lab_tests'

    id = Column(String, primary_key=True)
    lab_id = Column(String, nullable=False)
    lab_token = Column(String, nullable=False)
    lab_document = Column(JSON, nullable=False)
    patient_uuid = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LabTest(id='{self.id}', patient_uuid='{self.patient_uuid}')>"