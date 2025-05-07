# # backend/app/main.py
#
# from fastapi import FastAPI, HTTPException, Depends, status
# from sqlalchemy import text
# from sqlalchemy.orm import Session
#
# from db import models
# from db.database import engine, SessionLocal
# from db.models.user import User  # example import of your model
# from db.database import Base
#
# app = FastAPI(title="PotPie Assignment API")
#
# # Create all tables on startup
# models.Base.metadata.create_all(bind=engine)
# Base.metadata.create_all(bind=engine)
#
# def get_db() -> Session:
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
#
# @app.get("/test-db")
# def test_db_connection(db: Session = Depends(get_db)):
#     """
#     Executes a raw SELECT 1 to verify DB connectivity.
#     Returns 200 with {"db_status": "ok", "result": 1}.
#     """
#     try:
#         result = db.execute(text("SELECT 1")).scalar_one()
#         return {"db_status": "ok", "result": result}
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Database connection failed: {e}"
#         )
#
# @app.post("/users/", status_code=201)
# def create_user(username: str, email: str, db: Session = Depends(get_db)):
#     """
#     Simple endpoint to create a new user.
#     """
#     existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
#     if existing:
#         raise HTTPException(400, "Username or email already registered")
#     user = User(username=username, email=email)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return {"id": user.id, "username": user.username, "email": user.email}

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import models
from db.database import Base, engine, SessionLocal
from db.models.user import User  # example import of your model
from db.models.document import Document  # example import of your model
from api.document import router as docs_router
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Document Processing API")

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

@app.on_event("startup")
async def startup():
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/test-db")
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

app.include_router(docs_router)