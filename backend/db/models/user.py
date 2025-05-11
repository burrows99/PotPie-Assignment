# backend/db/models/user.py

from sqlalchemy import Column, Integer, String
from db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"<User(username={self.username!r}, email={self.email!r})>"
