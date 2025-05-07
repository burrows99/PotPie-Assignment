# backend/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use the psycopg2 sync driver and point at the Docker service name "database"
URL_DATABASE = "postgresql://postgres:mysecretpassword@database:5432/postgres"

# Create a sync engine with pre-ping for resiliency
engine = create_engine(
    URL_DATABASE,
    pool_pre_ping=True,
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()
