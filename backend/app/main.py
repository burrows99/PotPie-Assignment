from contextlib import asynccontextmanager
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
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
    # *Before* the app starts handling requests:
    # e.g. create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # *After* the app has shut down (cleanup)
    await engine.dispose()

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

app = FastAPI(
    title="Document Processing API",
    lifespan=lifespan,  # attach the lifespan manager
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(docs_router)
app.include_router(database_router)