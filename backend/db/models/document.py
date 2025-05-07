from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid, datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename      = Column(String, nullable=False)
    uploaded_at   = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_json = Column(JSON, nullable=True)
    text          = Column(Text, nullable=True)