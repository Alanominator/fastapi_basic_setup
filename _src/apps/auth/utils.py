from os import access
import re
import random
import string


from datetime import datetime, timedelta


from jose import JWTError, jwt
from jose.exceptions import JWTError

from core.config.settings import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

from core.utils import encrypt_string, decrypt_string

from core.config.database.database import SessionLocal

from typing import Union

from . import models
from . import exceptions



def isEmailValid(email: str):
    
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def isPasswordValid(password: str):
    if len(password) > 10 and password != "tesla":
        return True
    return False


def gen_string(length:int = 30) -> str:
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase  + string.digits) for _ in range(length))


def get_time_has_passed_by_epoch_in_min(epoch: int ):
    """
    Receives epoch int and returns difference between now
    """

    difference_sec = ( datetime.now() - datetime.fromtimestamp( epoch ) ).seconds

    difference_min = difference_sec / 60
    
    return difference_min


def create_auth_session_and_get_jwt_tokens(user_id: int):
    # todo get user where login and password is ///


    db = SessionLocal()


    # creating auth_session in database with tmp access jwt token
    db_auth_session = models.AuthSession(
        user_id = user_id,
        access_jwt_token = 'tmp'
    )

    db.add(db_auth_session)

    db.commit()
    # ______________


    # save auth session's id in variable
    db.refresh(db_auth_session)
    auth_session_id = db_auth_session.id
    # _____________


    # creating jwt tokens
    jwt_tokens = create_jwt_tokens(
        user_id = user_id,
        auth_session_id = auth_session_id
    )
    # _________


    # changing auth session's access jwt token in database
    access_token = jwt_tokens["access_token"]

    db_auth_session.access_jwt_token = access_token
    db.commit()
    # __________


    # close session
    db.close()

    return jwt_tokens






def create_jwt_tokens(
    user_id: str,
    auth_session_id: int
):

    payload = {
        "user_id": user_id,
        "session_id": encrypt_string( str(auth_session_id) ),
        "iat": datetime.utcnow(),
    }

    access_token = jwt.encode(
        claims = {
            **payload,
            "sub": "access_token"
        },
        key = SECRET_KEY,
        algorithm = ALGORITHM
    )

    refresh_token = jwt.encode(
        claims = {
            **payload,
            "sub": "refresh_token",
            "access_token": access_token
        },
        key = SECRET_KEY,
        algorithm = ALGORITHM
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }




def get_user_by_access_token(access_token: str):

    try:
        decoded_payload = jwt.decode(
            token = access_token,
            key = SECRET_KEY
        )
    except JWTError:
        raise exceptions.credentials_exception


    if get_time_has_passed_by_epoch_in_min(
        decoded_payload['iat']
    ) > ACCESS_TOKEN_EXPIRE_MINUTES:
        raise exceptions.credentials_exception


    session_id = decrypt_string(
        decoded_payload["session_id"]
    )

    db = SessionLocal()

    auth_session = db.query(models.AuthSession).where(
        models.AuthSession.id == session_id
    ).first()

    if not auth_session:
        raise exceptions.credentials_exception
    
    # verify access token with db
    if not auth_session.verify_access_jwt_token(access_token):
        raise exceptions.credentials_exception
        
    user_id = auth_session.user_id

    user = db.query(models.User).where(models.User.id == user_id).first()

    # check if the user is active
    if not user.is_active:
        raise exceptions.inactive_user

    db.close()

    return user




def refresh_jwt_tokens(refresh_token: str):
    try:
        decoded_payload = jwt.decode(
            token = refresh_token,
            key = SECRET_KEY
        )
    except JWTError:
        raise Exception("Todo")

    # check if it is a refresh token
    if not decoded_payload["sub"] == "refresh_token":
        raise Exception("Todo")


    # check if the token is expired
    if get_time_has_passed_by_epoch_in_min(
        decoded_payload['iat']
    ) > REFRESH_TOKEN_EXPIRE_MINUTES:
        raise exceptions.token_expired



    # create some vars
    session_id = decrypt_string(
        decoded_payload["session_id"]
    )

    access_token = decoded_payload["access_token"]

    db = SessionLocal()

    # get auth session from database
    auth_session = db.query(models.AuthSession).where(
        models.AuthSession.id == session_id
    ).first()


    # if doesn't exist, raise error
    if not auth_session:
        raise Exception("todo")
    

    # verify access token with db
    if not auth_session.verify_access_jwt_token(access_token):
        raise Exception("todo")


    # _________________________
    # here everything is ok


    # create new tokens
    new_jwt_tokens = create_jwt_tokens(
        user_id = auth_session.user_id,
        auth_session_id = auth_session.id
    )

    # update auth session's access_jwt_token in database
    new_access_token = new_jwt_tokens["access_token"]

    auth_session.access_jwt_token = new_access_token

    db.commit()

    # close db
    db.close()

    return new_jwt_tokens



