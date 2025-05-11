import uuid, datetime
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from db.database import Base

class Document(Base):
    __tablename__ = "documents"
    id            = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename      = Column(String, nullable=False)
    uploaded_at   = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_json = Column(JSON, nullable=True)
    text          = Column(Text, nullable=True)
