from pydantic import BaseModel, Field
from typing import Optional, Dict
from uuid import UUID
import datetime

class DocumentUpload(BaseModel):
    filename: str
    metadata: Optional[Dict] = Field(default_factory=dict)

class DocumentOut(BaseModel):
    id: UUID
    filename: str
    uploaded_at: datetime.datetime
    metadata_json: Optional[Dict]

class DocumentProcessIn(BaseModel):
    id: UUID