"""

database config settings

"""




from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

from dotenv import load_dotenv, find_dotenv
from .utils import get_env_var

# load env vars from .env file
load_dotenv(find_dotenv(
    filename='.env',
    raise_error_if_not_found=True
))



SQLALCHEMY_DATABASE_URL = get_env_var("DATABASE_URL")


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True
)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()
