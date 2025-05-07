import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:mysecretpassword@database:5432/postgres"
)

engine = create_async_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
