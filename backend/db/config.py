from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 1. Load your DATABASE_URL from env or fallback to a default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    # "jdbc:postgresql://localhost:5432/postgres"
    "postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/postgres"
)

# 2. Create the async engine
#    echo=True will log SQL; turn it off in production
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

# 3. Create a factory for AsyncSession
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # keep data after commit
)

# 4. Base class for your models
Base = declarative_base()
