from contextlib import asynccontextmanager
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sqlalchemy import text, inspect
from db import models
from db.database import Base, engine, SessionLocal
from db.models.user import User  # example import of your model
from db.models.document import Document  # example import of your model
from api.document import router as docs_router
from api.database import router as database_router
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    chroma = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings,
        collection_name="default_collection"
    )
    app.state.chroma = chroma
    yield
    await engine.dispose()

app = FastAPI(
    title="Document Processing API",
    lifespan=lifespan,  # attach the lifespan manager
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(docs_router)
app.include_router(database_router)