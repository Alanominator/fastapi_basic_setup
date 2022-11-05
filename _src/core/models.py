"""
Base models of project
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property

from core.base import Base


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True)

