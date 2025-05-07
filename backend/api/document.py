from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import SessionLocal
from db.schemas.document import DocumentOut, DocumentProcessIn
from services.document import ingest_document, process_document
import json

router = APIRouter(prefix="/api/docs", tags=["docs"])

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form("{}"),
    db: AsyncSession = Depends(get_db)
):
    try:
        metadata_dict = json.loads(metadata)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON")
    return await ingest_document(file, metadata_dict, db)

@router.post("/process")
async def process(doc_in: DocumentProcessIn, db: AsyncSession = Depends(get_db)):
    return await process_document(doc_in.id, db)