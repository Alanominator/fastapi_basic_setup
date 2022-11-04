"""

database config settings

"""




from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

from dotenv import load_dotenv, find_dotenv

# load env vars from .env file
load_dotenv(find_dotenv(
    filename='.env',
    raise_error_if_not_found=True
))


def get_env_var(key:str):
    """
    Gets environment variable.
    If it's None, raising Exception
    """
    var = os.getenv(key)
    if var != None:
        return var
    # var is None
    raise Exception(f'\n\n{key} is None.\n\n')


SQLALCHEMY_DATABASE_URL = get_env_var("DATABASE_URL")


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
