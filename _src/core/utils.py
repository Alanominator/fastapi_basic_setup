import os

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