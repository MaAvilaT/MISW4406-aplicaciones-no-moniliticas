from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class PartnerLab(Base):
    __tablename__ = 'partner_lab'

    id = Column(String, primary_key=True)
    lab_id = Column(String, nullable=False)
    lab_token = Column(String, nullable=False)

    def __repr__(self):
        return '<Lab %r>' % self.lab_id
