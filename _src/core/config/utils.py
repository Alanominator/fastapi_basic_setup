import os
from dotenv import load_dotenv, find_dotenv


def load_env():
    """
    load env vars from .env file

    call this function in every file where you need to get env var
    """
    load_dotenv(find_dotenv(
        filename='.env',
        raise_error_if_not_found=True
    ))



def get_env_var(key:str):
    """
    Gets environment variable.
    If it's None, raising Exception

    # But before do this
    load_env()
    """ 
    var = os.getenv(key)
    if var != None:
        return var
    # var is None
    raise Exception(f'\n\n{key} is None.\n\n')
