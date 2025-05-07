from typing import Dict, Any, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import SessionLocal
from db.schemas.document import DocumentOut, DocumentProcessIn
from services.document import ingest_document, process_document
from db.database import get_db

router = APIRouter(prefix="/api/database", tags=["docs"])

@router.get("/test")
async def test_db_connection(db: AsyncSession = Depends(get_db)):
    """
    Executes a raw SELECT 1 to verify DB connectivity.
    Returns 200 with {"db_status": "ok", "result": 1}.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        return {"db_status": "ok", "result": result.scalar_one()}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {e}"
        )


@router.get("/metadata", response_model=Dict[str, Any])
async def get_database_metadata(db: AsyncSession = Depends(get_db)):
    """
    Returns comprehensive metadata about the database including:
    - Available schemas
    - Tables in each schema
    - Columns for each table
    - Primary keys
    - Foreign keys
    """
    try:
        # Get database inspector
        inspector = inspect(db.get_bind())

        # Get all schemas
        schemas = await db.execute(text("SELECT schema_name FROM information_schema.schemata"))
        schema_names = [row[0] for row in schemas.fetchall()]

        metadata = {}

        for schema in schema_names:
            # Skip system schemas
            if schema in ['information_schema', 'pg_catalog']:
                continue

            metadata[schema] = {}

            # Get tables in schema
            tables = await db.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = :schema"),
                {"schema": schema}
            )
            table_names = [row[0] for row in tables.fetchall()]

            for table in table_names:
                metadata[schema][table] = {
                    "columns": [],
                    "primary_keys": [],
                    "foreign_keys": []
                }

                # Get columns
                columns = await db.execute(
                    text("""
                         SELECT column_name, data_type, is_nullable, column_default
                         FROM information_schema.columns
                         WHERE table_schema = :schema
                           AND table_name = :table
                         ORDER BY ordinal_position
                         """),
                    {"schema": schema, "table": table}
                )

                for col in columns.fetchall():
                    metadata[schema][table]["columns"].append({
                        "name": col[0],
                        "type": col[1],
                        "nullable": col[2] == 'YES',
                        "default": col[3]
                    })

                # Get primary keys
                pks = await db.execute(
                    text("""
                         SELECT column_name
                         FROM information_schema.key_column_usage
                         WHERE table_schema = :schema
                           AND table_name = :table
                           AND constraint_name IN (SELECT constraint_name
                                                   FROM information_schema.table_constraints
                                                   WHERE constraint_type = 'PRIMARY KEY'
                                                     AND table_schema = :schema
                                                     AND table_name = :table)
                         """),
                    {"schema": schema, "table": table}
                )

                metadata[schema][table]["primary_keys"] = [row[0] for row in pks.fetchall()]

                # Get foreign keys
                fks = await db.execute(
                    text("""
                         SELECT kcu.column_name,
                                ccu.table_name  AS foreign_table,
                                ccu.column_name AS foreign_column
                         FROM information_schema.key_column_usage kcu
                                  JOIN information_schema.constraint_column_usage ccu
                                       ON ccu.constraint_name = kcu.constraint_name
                         WHERE kcu.table_schema = :schema
                           AND kcu.table_name = :table
                           AND kcu.constraint_name IN (SELECT constraint_name
                                                       FROM information_schema.table_constraints
                                                       WHERE constraint_type = 'FOREIGN KEY'
                                                         AND table_schema = :schema
                                                         AND table_name = :table)
                         """),
                    {"schema": schema, "table": table}
                )

                metadata[schema][table]["foreign_keys"] = [
                    {
                        "column": row[0],
                        "references": f"{row[1]}({row[2]})"
                    }
                    for row in fks.fetchall()
                ]

        return metadata

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch database metadata: {str(e)}"
        )

@router.get("/tables", response_model=List[str])
async def get_all_tables(db: AsyncSession = Depends(get_db)):
    """
    Returns list of all tables in the database (excluding system tables)
    """
    try:
        result = await db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            AND table_schema NOT LIKE 'pg_%'
        """))
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch tables: {str(e)}"
        )

@router.get("/schemas", response_model=List[str])
async def get_all_schemas(db: AsyncSession = Depends(get_db)):
    """
    Returns list of all schemas in the database (excluding system schemas)
    """
    try:
        result = await db.execute(text("""
            SELECT schema_name 
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
            AND schema_name NOT LIKE 'pg_%'
        """))
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch schemas: {str(e)}"
        )