import os
from dotenv import load_dotenv, find_dotenv

import smtplib
from email.mime.text import MIMEText
from retry import retry

from enum import Enum
from typing import Union
from pydantic import validate_arguments

from passlib.context import CryptContext

from cryptography.fernet import Fernet

from .config import settings



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
    load_dotenv(find_dotenv(
        filename='.env',
        raise_error_if_not_found=True
    ))
    
    """ 
    var = os.getenv(key)
    if var != None:
        return var
    # var is None
    raise Exception(f'\n\n{key} is None.\n\n')





import fastapi
from typing import List
from pydantic import validate_arguments

# @validate_arguments
def include_routers(application: fastapi.applications.FastAPI, routers_to_include: List[fastapi.routing.APIRouter]):
    assert isinstance(application, fastapi.applications.FastAPI)
    for r in routers_to_include:
        assert isinstance(r, fastapi.routing.APIRouter)

    for r in routers_to_include:
        application.include_router(r)





@validate_arguments
def send_email(
    *,
    message: str,
    message_type: str = "plain",
    message_subject: str = None,
    recipients: Union[str, list],
    delay: Union[int, float] = 5,
    tries: int = 5
):
    """
    Function that sends email message.
    """

    # ! GLOBAL SETTINGS
    sender = "jw6907029@gmail.com"
    password = "xmrcgbsixwplquqy"
    # ! ||||||||||||||||||||||||||

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    @retry(delay = delay, tries = tries)
    def _main():
        try:
            server.login(sender, password)

            msg = MIMEText(message, message_type) #
            msg["Subject"] = message_subject

            server.sendmail(
                from_addr = sender,
                to_addrs = recipients,
                msg = msg.as_string()
            )

        except Exception as _ex:
            print(_ex)
            raise Exception()

    try:
        _main()
        print("Message has been sent")
    except Exception as _ex:
        print(f"{_ex}\tEmail has not been sent.")



_pwd_context = CryptContext(schemes=[
    "pbkdf2_sha256",
    "md5_crypt"
], deprecated="auto")


def hash_string(plain_text: str) -> str:
    return _pwd_context.hash(plain_text)


def verify_hashed_string(plain_string: str, hashed_string: str) -> bool:
    return _pwd_context.verify(
        secret = plain_string, 
        hash = hashed_string
    )



_fernet = Fernet(settings.SECRET_KEY)


def encrypt_string(string: str) -> str:
    return _fernet.encrypt( 
        string.encode()
    ).decode()

def decrypt_string(string: str) -> str:
    return _fernet.decrypt(string).decode()



