from celery_app import celery
from jinja2 import Environment, FileSystemLoader
from core.utils import send_email
from . import crud
from typing import Union

from core.config.database.database import SessionLocal


from . import models




@celery.task
def send_activation_link(recipients: Union[str, list], token: str):
    
    environment = Environment(loader=FileSystemLoader("apps/auth/templates/activate_account"))
    template = environment.get_template("activate_account.html")

    message = str(template.render({
        "token": token
    }))


    send_email(
        message= message,
        message_type="html",
        message_subject="Subject",
        recipients=recipients
    )



@celery.task
def register_task(*,
    email: str,
    password: str
):


    db = SessionLocal()


    # create user
    db_user = crud.create_user(db,
        email = email,
        password = password
    )

    # create token
    db_token = crud.create_activation_token(db, 
        user_id = db_user.id
    )

    # send email
    email = db_user.email
    token = db_token.token

    user_id = db_user.id

    db.close()


    send_activation_link.delay(
        recipients = email,
        token = token
    )

    # 
    delete_user_by_id_if_not_active.apply_async( 
        kwargs = {"id": user_id}, 
        countdown = min_to_sec(DELETE_INACTIVE_USER_TIMEOUT_MIN)
    )


DELETE_INACTIVE_USER_TIMEOUT_MIN = 7


def min_to_sec(min):
    return min * 60


@celery.task
def delete_user_by_id_if_not_active(id):
    db = SessionLocal()

    user = db.query(models.User).\
        where(models.User.id == id).\
            first()
    
    if user:
        if not user.is_active:
            db.delete(user)
            db.commit()

    db.close()