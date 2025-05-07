import uuid
from fastapi import UploadFile, HTTPException
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.document import Document

# Use HuggingFace local embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

async def ingest_document(file: UploadFile, metadata: dict, db: AsyncSession):
    content = await file.read()
    text = content.decode('utf-8', errors='ignore')

    doc = Document(
        filename=file.filename,
        metadata_json=metadata,
        text=text
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc

async def process_document(doc_id: uuid.UUID, db: AsyncSession, persist_directory: str = "chroma_db"):
    document = await db.get(Document, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_text(document.text)

    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=str(doc_id),
    )
    ids = [f"{doc_id}-{i}" for i in range(len(chunks))]
    vectordb.add_texts(texts=chunks, ids=ids)
    vectordb.persist()

    return {"indexed_chunks": len(chunks)}