from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import declarative_base

from core.base import Base



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(40), unique=True, index=True)
    _password_hash = Column("password", String())
    created_at = Column(DateTime(), server_default=func.now())

    @hybrid_property
    def password(self):
        return self._password_hash
    
    @password.setter
    def password(self, plain):
        self._password_hash = f"fakehash-{plain}"
