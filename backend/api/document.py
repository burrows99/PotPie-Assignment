from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import SessionLocal
from db.schemas.document import DocumentOut, DocumentProcessIn
from services.document import ingest_document, process_document
import json
from db.database import get_db

router = APIRouter(prefix="/api/docs", tags=["docs"])

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

@router.post("/process", response_model=None)
async def process_document_endpoint(
    request: Request,
    doc_in: DocumentProcessIn,
    db: AsyncSession = Depends(get_db)
):
    chroma = request.app.state.chroma
    return await process_document(doc_in.id, db, chroma)