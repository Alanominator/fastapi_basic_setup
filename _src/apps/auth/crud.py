from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from . import models





def create_user(db: Session, email, password, is_active: bool = False):
    db_user = models.User(
        email=email,
        password = password,
        is_active = is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user



def get_user_by_email(db: Session, email: str):
    return db.query(models.User).\
        filter(models.User.email == email).\
            first()



# def update_user(db: Session, user, values_to_update: dict):
#     db.add(user)

#     # user.update()

#     for key in values_to_update:


#     # 

#     db.commit()



def create_activation_token(db: Session, user_id: int):
    db_token = models.ActivationToken(
        user_id = user_id
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token


def get_activation_token_by_user_id(db: Session, user_id):
    db_token = db.query(models.ActivationToken).\
        filter(models.ActivationToken.user_id == user_id).\
            first()

    return db_token


def get_activation_token_by_token(db: Session, token):
    db_token = db.query(models.ActivationToken).\
        filter(models.ActivationToken.token == token).\
            first()
        
    return db_token

# def delete_activation_token(db: Session, id):





