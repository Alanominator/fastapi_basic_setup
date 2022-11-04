"""
Base models of project
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from .base import Base

class Test(Base):
   __tablename__ = "test"

   id = Column(Integer, primary_key=True, index=True)
   first_name = Column(String,)
   last_name = Column(String)
   age = Column(Integer)
